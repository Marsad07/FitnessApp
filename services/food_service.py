import json
import requests as req
import os
from app import db
from dotenv import load_dotenv
from os.path import join, dirname
from app.models.food_cache_model import FoodCache

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)                                # load_dotenv() reads variables from a .env file

url = ("https://api.nal.usda.gov/fdc/v1/foods/search")    # Built URL for USDA FoodData

def check_foodcache(query):
    # 1) Check if a cache row already exists for this exact search term
    result = FoodCache.query.filter(FoodCache.search_term == query).first()

    #2) Cache MISS = nothing saved yet for this search term
    if result is None:
        # Gets fresh data from USDA, same as normal
        new_data = search_food(query)

        # Build a new cache row - store the search term as-is, and
        # convert the dictionary into text (json.dumps) so it can fit
        # into a plain text column
        search_term = FoodCache(
            search_term=query,
            results=json.dumps(new_data)
        )
        db.session.add(search_term)
        db.session.commit()

        # Return the fresh data, exactly like search_food() normally would
        return new_data
    else:
        # 3) cache HIT = a row already exists, no need to call USDA again
        # Converts the stored text back into a real dictionary (reverses json.dumps)
        results = json.loads(result.results)
        return results

def search_food(query):
    api_key = os.getenv('USDA_API_KEY')  # os.getenv gets variable specified + returns none if dont exist
    food = req.get(url, params={"api_key": api_key, "query": query})

    macros = {}  # Macros dict to store specific nutrients + values

    foods_list = food.json()["foods"] # foods_list is for the massive list of results for a query
    nutrient_list = foods_list[0]["foodNutrients"]  # Stores full list of food nutrients from first result
    food_desc = foods_list[0]["description"]  # Stores food description from first result

    # To loop through nutrient_list and pick out specific nutrients + their values
    for nutrient in nutrient_list:
        if nutrient["nutrientId"] == 1004:
            macros["fat"] = nutrient["value"]

        if nutrient["nutrientId"] == 1008:
            macros["energy"] = nutrient["value"]

        if nutrient["nutrientId"] == 1003:
            macros["protein"] = nutrient["value"]

        if nutrient["nutrientId"] == 1005:
            macros["carbs"] = nutrient["value"]
    macros["description"] = food_desc
    return macros

