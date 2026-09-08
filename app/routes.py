from .models.logged_entry_model import LoggedEntry
from app import db
from flask import Blueprint
from services.food_service import search_food


bp1 = Blueprint('search', __name__, url_prefix='/routes')

@bp1.route('/search', methods=['GET'])
def search_food_results():
    # Call the USDA API service to get nutrition data for a food
    # (hardcoded to "apple" for now, until  real search form exists)
    result = search_food("apple")

    new_entry = LoggedEntry(               # Build a new LoggedEntry object, mapping each database column
    # to its correct source: API data, or a placeholder until a real form exists
        food_name=result["description"],   # from the API's dict
        food_weight=100.50,                # placeholder - no form yet
        calories=result["energy"],         # from the API's dict
        protein=result["protein"],
        carbs=result["carbs"],
        fats=result["fat"],
        meal_category="breakfast",         # placeholder - no form yet
    )

    # Stage the new entry, then actually save it to the database
    db.session.add(new_entry)
    db.session.commit()

    success = "Macros saved into db"
    return success