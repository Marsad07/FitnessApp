from .models.logged_entry_model import LoggedEntry
from app import db
from flask import Blueprint, request, render_template
from services.food_service import search_food


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


    result = search_food(food_name)        # Used to be hardcoded, now contains real variable
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
    new_entry = LoggedEntry.query.all()
    diary_data = []

    for entry in new_entry:
        diary_data.append({"food_name": entry.food_name, "food_weight": entry.food_weight, "calories": entry.calories,
                           "protein": entry.protein, "carbs": entry.carbs, "fats": entry.fats,
                           "meal_category": entry.meal_category})
    return diary_data
