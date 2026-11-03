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
    try:
        food = req.get(url, params={"api_key": api_key, "query": query}, timeout=10)

    except req.exceptions.RequestException:
        return None

    if food.status_code != 200:
        return None

    macros = {}  # Macros dict to store specific nutrients + values

    foods_list = food.json()["foods"] # foods_list is for the massive list of results for a query
    if not foods_list:
        return None
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

def get_food_options(query):
    api_key = os.getenv('USDA_API_KEY')
    try:
        food = req.get(url, params={"api_key": api_key, "query": query}, timeout=10)
    except req.exceptions.RequestException:
        return None
    if food.status_code != 200:
        return None

    foods_list = food.json()["foods"]  # Every food USDA returned for this search

    foods = []  # Holds a small, clean version of each food (just name + id)
    for item in foods_list:
        food_desc = item["description"]
        fdcId = item["fdcId"]
        foods.append({"fdcId": fdcId, "description": food_desc})
    return foods  # A short list which results page can display

def fetch_food_details(fdc_id):
    # 1) Builds the URL for this one specific food (id goes in the path, not params)
    api_key = os.getenv('USDA_API_KEY')
    detail_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
    try:
        food = req.get(detail_url,  params={"api_key": api_key,}, timeout=10)
    except req.exceptions.RequestException:
        return None


    # This checks if USDA actually found this food (200 = found, anything else
    # like 404 = not found or USDA had a problem), if not, sends back None
    # so the route can tell the user instead of crashing
    if food.status_code != 200:
        return None

    # 2) Get the food's name and its full nutrient list directly (no [0] needed here)
    food_desc = food.json()["description"]
    nutrient_list = food.json()["foodNutrients"]
    macros = {}

    # 3) Loops through nutrients, safely checks each one's id (some entries
    # don't have the expected shape, so .get() is implemented prevents crashing)
    for nutrient in nutrient_list:
        if nutrient.get("nutrient", {}).get("id") == 1004:
            macros["fat"] = nutrient.get("amount", 0)

        if nutrient.get("nutrient", {}).get("id") == 1008:
            macros["energy"] = nutrient.get("amount", 0)

        if nutrient.get("nutrient", {}).get("id") == 1003:
            macros["protein"] = nutrient.get("amount", 0)

        if nutrient.get("nutrient", {}).get("id") == 1005:
            macros["carbs"] = nutrient.get("amount", 0)

    # 4) Combines name + macros into one result and returns it
    macros["description"] = food_desc
    return macros


