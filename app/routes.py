import json
from flask import Blueprint
from services.food_service import search_food
bp1 = Blueprint('search', __name__, url_prefix='/routes')

@bp1.route('/search', methods=['GET'])
def search_food_results():
    result = search_food("apple")
    return result