from werkzeug.utils import redirect
from .models.logged_entry_model import LoggedEntry
from app import db
from flask import Blueprint, request, render_template, session, flash, url_for
from services.food_service import search_food, check_foodcache, get_food_options, fetch_food_details
from datetime import date, datetime, timedelta
from app.decorators import login_required

food_bp = Blueprint('search', __name__, url_prefix='/routes')

@food_bp.route('/search', methods=['GET'])
def search_food_results():
    # Call the USDA API service to get nutrition data for a food
    # Form values
    food_name = request.args.get('food_name')
    if food_name is None:
        return render_template('online/foods/search.html')

    result = get_food_options(food_name)   # Used to be hardcoded, now contains real variable
    return render_template('online/foods/food_search_list.html', foods=result)

@food_bp.route('/diary_view', methods=['GET'])
@login_required # Decorator to check if users logged in
def full_diary_view():
    # Reads users ID from session
    user_id = session.get('user_id')

    # Built the two boundary points: midnight today, and midnight tomorrow
    today_start = datetime.combine(date.today(), datetime.min.time())
    tomorrow_start = today_start + timedelta(days=1)

    # Only gets entries logged between those three boundaries (for e.g: today only)
    today_diary = LoggedEntry.query.filter(LoggedEntry.logged_at >= today_start,
                                           LoggedEntry.logged_at < tomorrow_start,
                                           LoggedEntry.user_id == user_id).all()

    # todays_entries holds each individual food logged today, separately
    # the four total_X variables track the running sum across all of them
    todays_entries = []
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fats = 0

    # One loop doing two jobs at once: built the individual entry list,
    # And added each entry's values onto the running totals
    for entry in today_diary:
        todays_entries.append({"entry_id": entry.id, "food_name": entry.food_name,
                               "food_weight": entry.food_weight,
                               "calories": entry.calories, "protein": entry.protein,
                               "carbs": entry.carbs, "fats": entry.fats,
                               "meal_category": entry.meal_category})
        total_calories=total_calories + entry.calories
        total_protein=total_protein + entry.protein
        total_carbs=total_carbs + entry.carbs
        total_fats=total_fats + entry.fats

    # Sends both the individual entries and the final totals to the template
    return render_template("online/diary/diary_view.html", todays_entries=todays_entries,
                           total_calories=total_calories,
                           total_protein=total_protein,
                           total_carbs=total_carbs,
                           total_fats=total_fats)

@food_bp.route('/food_chosen', methods=['GET'])
@login_required # Decorator to check if users logged in
def food_chosen():
    # Reads users ID from session
    user_id = session.get('user_id')

    # Gets the food's unique ID (always present, from the results list link)
    fdc_Id = request.args.get('fdcId')
    # meal_category only exists once the small details form has been submitted
    meal_category = request.args.get('meal_category')

    # Moment 1: just clicked a result, meal_category/food_weight not chosen yet
    if meal_category is None:
        return render_template('/online/foods/food_details_form.html', fdc_id=fdc_Id)
    else:
        # Moment 2: the details form was submitted, everything needed is here now
        food_weight = request.args.get('food_weight')

        # Tries to turn the weight from text into a decimal number so it can be used for equation
        try:
            food_weight = float(food_weight)
        # If it can't be turned into a number (empty box or letters = ValueError,
        # weight missing from the url completely = TypeError), tells the user and
        # sends them back to the same food form
        except (ValueError, TypeError):
            flash('Invalid input, Enter a number for food weight!')
            return redirect(url_for('search.food_chosen', fdcId=fdc_Id))

        # 2) By this point it's definitely a number, so it's safe to compare it to 0
        # It rejects 0 or negative weights before calling USDA or saving anything
        if food_weight <= 0:
            flash('Invalid input, Enter a number bigger than 0 for food weight!')
            return redirect(url_for('search.food_chosen', fdcId=fdc_Id))

        # Fetches full, real details for this specific food
        details = fetch_food_details(fdc_Id)

        if details is None:
            flash('No details found for this food!')
            return redirect(url_for('search.search_food_results'))


        # Builds the actual entry to save with user id - the macro fields are scaled by the weight entered,
        # Since USDA gives values per 100g: (value from the API * weight) / 100.
        # Each one uses .get() with a fallback of 0 so missing USDA data doesn't crash it.
        # meal_category/food_weight come straight from the form
        new_entry = LoggedEntry(
            user_id = user_id,
            food_name = details.get('description', "Unknown Food"),
            calories = food_weight * details.get('energy', 0) / 100,
            protein = food_weight * details.get('protein', 0) / 100,
            carbs = food_weight * details.get('carbs', 0) / 100,
            fats = food_weight * details.get('fat', 0) / 100,

            meal_category = meal_category,
            food_weight = food_weight,
        )

        # Saves it
        db.session.add(new_entry)
        db.session.commit()

    # Shows the confirmation page
    return render_template("/online/foods/search_confirmation.html", new_entry=new_entry)

@food_bp.route('/delete_entry', methods=['POST'])
@login_required # Decorator to check if users logged in
def delete_entry():
    # Reads users ID from session
    user_id = session.get('user_id')

    # Gets specific entry id from the form
    entry_id = request.form.get('id')

    # Looks up that specific entry, returns none if it don't exist
    # And second condition only matches if the entry belongs to that user
    result = LoggedEntry.query.filter(LoggedEntry.id == entry_id, LoggedEntry.user_id == user_id ).first()

    # If there's nothing to delete, tells user via flash message and sends them back
    if result is None:
        flash('This food does not exist')
        return redirect(url_for('search.full_diary_view'))
    # This actually deletes it and makes it permanent
    else:
        db.session.delete(result)
        db.session.commit()
        flash('This food has now been deleted')
        return redirect(url_for('search.full_diary_view'))

@food_bp.route('/edit_entry', methods=['GET', 'POST'])
@login_required # Decorator to check if users logged in
def edit_entry():
    # Reads users ID from session
    user_id = session.get('user_id')

    # Gets the entry id from the right place: the hidden input when the form is submitted (POST),
    # or the url when the Edit link was just clicked (GET)
    if request.method == 'POST':
        entry_id = request.form.get('id')
    else:
        entry_id = request.args.get('id')

    # This was done the same way in delete_entry function
    # (second condition only matches if the entry belongs to that user)
    result = LoggedEntry.query.filter(LoggedEntry.id == entry_id, LoggedEntry.user_id == user_id).first()

    # If the entry doesn't exist, tell the user and go back to the diary
    if result is None:
        flash('This food does not exist')
        return redirect(url_for('search.full_diary_view'))

    # Moment 1: Edit link was just clicked, where nothing submitted yet,
    # So show the form with the entry's current values pre-filled
    if request.method == 'GET':
        return render_template("/online/foods/food_details_form.html", entry_id=entry_id,
                               food_name=result.food_name, food_weight=result.food_weight,
                               meal_category=result.meal_category)

    # Moment 2: This is where the form was submitted with new values
    meal_category = request.form.get('meal_category')
    food_weight = request.form.get('food_weight')

    # Since form values are text, this converts the new weight to a number
    # (an empty or non-number box = ValueError, a missing box = TypeError, both are caught here)
    try:
        new_food_weight = float(food_weight)
    except (ValueError, TypeError):
        flash('Please enter a number for the food weight!')
        return redirect(url_for('search.full_diary_view'))

    # This rejects 0 or negative weights BEFORE changing anything
    if new_food_weight <= 0:
        flash('You cannot put 0 for food weight, Please enter a number bigger than 0!')
        return redirect(url_for('search.full_diary_view'))

    # This retrieves the old weight (treated as 0 if nothing was saved)
    old_food_weight = float(result.food_weight or 0)

    # This can only scale if there's an old weight to scale from (since dividing by 0 would crash)
    if old_food_weight > 0:
        # Scales calories, protein, carbs and fats from the old weight to the new weight
        result.calories = float(result.calories or 0) * new_food_weight / old_food_weight
        result.protein = float(result.protein or 0) * new_food_weight / old_food_weight
        result.carbs = float(result.carbs or 0) * new_food_weight / old_food_weight
        result.fats = float(result.fats or 0) * new_food_weight / old_food_weight
        message = 'This food has now been edited'
    else:
        message = 'Weight updated, but the macros could not be rescaled because the old weight was 0'

    # This updates the entry that's already been looked up
    result.food_weight = new_food_weight
    result.meal_category = meal_category

    db.session.commit()
    flash(message)
    return redirect(url_for('search.full_diary_view'))