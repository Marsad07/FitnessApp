from app import create_app
from services.food_service import search_food, fetch_food_details
from dotenv import load_dotenv
from os.path import join, dirname
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)                                # load_dotenv() reads variables from a .env file

app = create_app()

if __name__ == '__main__':
    fdcId = 2038064
    result = fetch_food_details(fdcId)
    print(result)
    #app.run(debug=True)