import json
from datetime import datetime, timedelta
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
    # 1) Cleans up the search term so "Uppercaseterm " and "lowercaseterm" share one cache row
    query = query.strip().lower()

    # 2) Looks up the cache row for the cleaned term to store in a variable!
    result = FoodCache.query.filter(
        FoodCache.search_term == query
    ).first()

    # 3) Cache HIT + still fresh (row exists and saved less than 30 days ago)
    # it return the saved results, no USDA call needed
    if (
        result is not None
        and result.cached_at > datetime.now() - timedelta(days=30)
    ):
        return json.loads(result.results)

    # 4) Cache MISS or expired -> get fresh USDA data
    new_data = get_food_options(query)

    # 5) USDA failed -> returns None + doesnt save
    if new_data is None:
        return None

    # 6) Saves fresh results and updates old row if one exists, otherwise makes a new row
    if result is not None:
        result.results = json.dumps(new_data)
        result.cached_at = datetime.now()
    else:
        result = FoodCache(
            search_term=query,
            results=json.dumps(new_data)
        )
        db.session.add(result)
    db.session.commit()

    # 7) Return fresh results
    return new_data

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


