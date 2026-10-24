from sqlalchemy import result_tuple
from werkzeug.utils import redirect
from .models.logged_entry_model import LoggedEntry
from app import db
from flask import Blueprint, request, render_template, session, flash, url_for
from services.food_service import search_food, check_foodcache, get_food_options, fetch_food_details
from datetime import date, datetime, timedelta

bp1 = Blueprint('search', __name__, url_prefix='/routes')

@bp1.route('/search', methods=['GET'])
def search_food_results():
    # Call the USDA API service to get nutrition data for a food
    # Form values
    food_name = request.args.get('food_name')
    if food_name is None:
        return render_template('online/foods/search.html')

    result = get_food_options(food_name)   # Used to be hardcoded, now contains real variable
    return render_template('online/foods/food_search_list.html', foods=result)

@bp1.route('/diary', methods=['GET'])
def view_diary():
    # Gets every logged entry from the database, no filtering
    new_entry = LoggedEntry.query.all()
    diary_data = []

    # Go through each entry one at a time, pull out its real values
    # (dot notation since these are real objects, not dictionaries),
    # and build a clean dictionary per entry, added to the list
    for entry in new_entry:
        diary_data.append({"food_name": entry.food_name, "food_weight": entry.food_weight, "calories": entry.calories,
                           "protein": entry.protein, "carbs": entry.carbs, "fats": entry.fats,
                           "meal_category": entry.meal_category})
    return diary_data

@bp1.route('/diary_today', methods=['GET'])
def diary_today():
    # Build the two boundary points: midnight today, and midnight tomorrow
    today_start = datetime.combine(date.today(), datetime.min.time())
    tomorrow_start = today_start + timedelta(days=1)

    # Running totals, all starting at 0 before the loop adds anything on
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fats = 0

    # Only get entries logged between those two boundaries (i.e. today only)
    today_diary = LoggedEntry.query.filter(LoggedEntry.logged_at >= today_start,
                                           LoggedEntry.logged_at < tomorrow_start).all()

    # Add each entry's values onto the running totals, one at a time
    for entry in today_diary:
        total_calories=total_calories + entry.calories
        total_protein=total_protein + entry.protein
        total_carbs=total_carbs + entry.carbs
        total_fats=total_fats + entry.fats

    # Combine all four final totals into one dictionary and send it back
    total_macros = {"calories": total_calories, "protein": total_protein, "carbs": total_carbs, "fats": total_fats}
    return total_macros

@bp1.route('/diary_view', methods=['GET'])
def full_diary_view():
    # Built the two boundary points: midnight today, and midnight tomorrow
    today_start = datetime.combine(date.today(), datetime.min.time())
    tomorrow_start = today_start + timedelta(days=1)

    # Only gets entries logged between those two boundaries (for e.g: today only)
    today_diary = LoggedEntry.query.filter(LoggedEntry.logged_at >= today_start,
                                           LoggedEntry.logged_at < tomorrow_start).all()

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
        todays_entries.append({"entry_id": entry.id, "food_name": entry.food_name, "food_weight": entry.food_weight,
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

@bp1.route('/food_chosen', methods=['GET'])
def food_chosen():
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

        # Builds the actual entry to save - the macro fields are scaled by the weight entered,
        # Since USDA gives values per 100g: (value from the API * weight) / 100.
        # Each one uses .get() with a fallback of 0 so missing USDA data doesn't crash it.
        # meal_category/food_weight come straight from the form
        new_entry = LoggedEntry(
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

@bp1.route('/delete_entry', methods=['GET'])
def delete_entry():
    # Gets specific entry id from the url
    entry_id = request.args.get('id')

    # Looks up that specific entry, returns none if it don't exist
    result = LoggedEntry.query.filter(LoggedEntry.id == entry_id).first()

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

@bp1.route('/edit_entry', methods=['GET'])
def edit_entry():
    # Gets entry id from the url (same way delete_entry function does)
    entry_id = request.args.get('id')

    # This only exists once the edit form has been submitted, so it's None the first time
    food_weight = request.args.get('food_weight')

    # This was done the same way in delete_entry function
    result = LoggedEntry.query.filter(LoggedEntry.id == entry_id).first()

    # If the entry doesn't exist, tell the user and go back to the diary
    if result is None:
        flash('This food does not exist')
        return redirect(url_for('search.full_diary_view'))

    # Moment 1: Edit link was just clicked, where nothing submitted yet,
    # So show the form with the entry's current values pre-filled
    if food_weight is None:
        return render_template("/online/foods/food_details_form.html", entry_id=entry_id,
                               food_name=result.food_name, food_weight=result.food_weight,
                               meal_category=result.meal_category)

    # Moment 2: This is where the form was submitted with new values
    else:
        meal_category = request.args.get('meal_category')

        # Since form values are text, this converts the new weight to a number
        # (an empty or non-number box would cause a crash to float(), so it's caught here)
        try:
            new_food_weight = float(food_weight)
        except ValueError:
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