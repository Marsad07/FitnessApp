from .models.logged_entry_model import LoggedEntry
from app import db
from flask import Blueprint, request, render_template
from services.food_service import search_food, check_foodcache
from datetime import date, datetime, timedelta

bp1 = Blueprint('search', __name__, url_prefix='/routes')

@bp1.route('/search', methods=['GET'])
def search_food_results():
    # Call the USDA API service to get nutrition data for a food
    # Form values
    food_name = request.args.get('food_name')
    if food_name is None:
        return render_template('online/foods/search.html')
    meal_category = request.args.get('meal_category')
    food_weight = request.args.get('food_weight')
    food_weight = float(food_weight)


    result = check_foodcache(food_name)        # Used to be hardcoded, now contains real variable
    new_entry = LoggedEntry(               # Build a new LoggedEntry object, mapping each database column,
        food_name=result.get("description", "unknown food"),
        food_weight=food_weight,
        calories=result.get("energy", 0),
        protein=result.get("protein",0),
        carbs=result.get("carbs",0),
        fats=result.get("fat", 0),
        meal_category=meal_category,
    )

    # Stage the new entry, then actually save it to the database
    db.session.add(new_entry)
    db.session.commit()

    success = "Macros saved into db"
    return success

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
        todays_entries.append({"food_name": entry.food_name, "food_weight": entry.food_weight, "calories": entry.calories,
                           "protein": entry.protein, "carbs": entry.carbs, "fats": entry.fats,
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



