import requests as req
import os
import json
from dotenv import load_dotenv
from os.path import join, dirname
from json import dumps


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)                                # load_dotenv() reads variables from a .env file
api_key = os.getenv('USDA_API_KEY')                     # os.getenv gets variable specified + returns none if dont exist

url = ("https://api.nal.usda.gov/fdc/v1/foods/search")    # Built URL
food = req.get(url, params={"api_key": api_key, "query": "Banana"})

foods_list = food.json()["foods"]
#print(json.dumps(foods_list[0], indent=4))

nutrient_list = foods_list[0]["foodNutrients"]
macros = {}
for nutrient in nutrient_list:
    if nutrient["nutrientId"] == 1004:
        macros["fat"] = nutrient["value"]

    if nutrient["nutrientId"] == 1008:
        macros["energy"] = nutrient["value"]

    if nutrient["nutrientId"] == 1003:
        macros["protein"] = nutrient["value"]

    if nutrient["nutrientId"] == 1005:
        macros["carbs"] = nutrient["value"]


print(macros)
#print(json.dumps(nutrient_list[0], indent=4))