from app import create_app
from services.food_service import  fetch_food_details
from dotenv import load_dotenv
from os.path import join, dirname
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)                                # load_dotenv() reads variables from a .env file

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)