# Griot Fitness

A calorie and macro tracker built with Flask. Search real foods from the USDA FoodData Central database, log what you eat by the gram, and see your calories, protein, carbs and fats add up against your own daily goals.

![Dashboard](screenshots/dashboard.png)

## Features

- **Accounts** – register, log in and log out. Passwords are hashed, and each user only ever sees their own data.
- **Food search** – search the USDA FoodData Central database and pick the closest match.
- **Log by weight** – enter how many grams you had and the calories and macros are scaled to match.
- **Nutrition page** – everything logged for the day, grouped into breakfast, lunch, dinner and snack, with a calorie subtotal for each meal.
- **Past days** – step back through previous days with Previous / Next day links.
- **Daily goals** – set calorie, protein, carbs and fats targets and track progress with bars.
- **Dashboard** – today's calories as a progress ring, macro bars, and how much is left (or how far over).
- **Edit and delete** – change the weight or meal of any entry, with macros rescaled automatically.
- **Search caching** – repeat searches come from a 30-day cache instead of calling USDA again, so popular searches keep working even if the API is down.
- **Responsive design** – sidebar layout on laptops, bottom tab bar on phones.

## Built with

- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Database:** MySQL
- **API:** [USDA FoodData Central](https://fdc.nal.usda.gov/api-guide)
- **Frontend:** Jinja templates, Tailwind CSS, animate.css

## Screenshots

| Nutrition | Logging a food |
|---|---|
| ![Nutrition](screenshots/nutrition.png) | ![Log food](screenshots/log_food.png) |

## Running it locally

1. **Clone the repo**
   ```bash
   git clone https://github.com/Marsad07/FitnessApp.git
   cd FitnessApp
   ```

2. **Create a virtual environment and install the requirements**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   # source .venv/bin/activate   # Mac / Linux
   pip install -r requirements.txt
   ```

3. **Get a free USDA API key** from [api.data.gov/signup](https://api.data.gov/signup/).

4. **Create a `.env` file** in the project folder with these keys:
   ```
   DB_HOST=localhost
   DB_USER=your_mysql_user
   DB_PASSWORD=your_mysql_password
   DB_NAME=fitnessapp_db
   SECRET_KEY=any_long_random_string
   USDA_API_KEY=your_usda_api_key
   ```

5. **Create the database** by running `database/schema.sql` in MySQL Workbench (or the `mysql` command line).

6. **Run the app**
   ```bash
   flask --app main run
   ```
   Then open http://127.0.0.1:5000.

## Project structure

```
FitnessApp/
├── main.py                 # Loads .env and starts the app
├── app/
│   ├── __init__.py         # create_app(), database setup, homepage / dashboard route
│   ├── routes.py           # Search, logging, nutrition, goals, edit and delete
│   ├── auth_routes.py      # Register, login, logout
│   ├── decorators.py       # @login_required
│   ├── models/             # User, LoggedEntry, Nutrition (goals), FoodCache
│   ├── templates/          # Jinja templates
│   └── static/css/         # Extra CSS (animations)
├── services/
│   └── food_service.py     # USDA API calls + search cache
└── database/
    └── schema.sql          # Creates all the tables
```

## What I learned

- **Never trusting user input** – every form value is checked on the server, even with `required` in the HTML, because browser checks can be bypassed.
- **Ownership checks** – every query filters by the logged-in user's ID from the session, so changing an ID in the URL can't reach someone else's data.
- **Talking to an external API safely** – timeouts, catching network errors, and telling "the API failed" apart from "nothing was found".
- **Caching** – normalising the search term, expiring old results, and never caching a failure.
- **Refactoring** – moving shared logic into one helper (`get_day_summary`) so the dashboard and nutrition page always show the same numbers.

## What's next

- Automated tests with pytest
- Deploying a live version
- Logging food to past days, and a 7-day calorie history chart
