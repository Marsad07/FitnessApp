import os
from datetime import date, datetime, timedelta
from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    from .routes import food_bp
    from .auth_routes import auth_bp

    app.register_blueprint(food_bp)
    app.register_blueprint(auth_bp)

    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    secret_key = os.getenv('SECRET_KEY')

    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}"
    app.config['SECRET_KEY'] = secret_key
    db.init_app(app)

    # Homepage - logged out users see the landing page, logged in users see their dashboard
    @app.route('/')
    def homepage():
        # Imported here (not at the top) to avoid a circular import, since the models and routes import db from this file
        from .models.user_accounts_model import User
        from .routes import get_day_summary

        # 1) Not logged in -> landing page with sign up / log in
        user_id = session.get('user_id')
        if user_id is None:
            return render_template('/online/homepage/homepage.html')

        # If the user in the session no longer exists (e.g. account deleted), log them out and show the landing page
        user = db.session.get(User, user_id)
        if user is None:
            session.pop('user_id', None)
            return render_template('/online/homepage/homepage.html')

        # 2) Gets today's entries, totals and goals from the same helper the nutrition page uses,
        # so the dashboard and nutrition page always show the same numbers
        today = date.today()
        summary = get_day_summary(user_id, today)

        # 3) Builds the date shown in the greeting e.g. "Mon 2 Nov" - .day is used instead of %-d,
        # since %-d crashes on Windows
        date_label = f"{today.strftime('%a')} {today.day} {today.strftime('%b')}"

        return render_template('/online/dashboard/online_dashboard.html',
                               username=user.username,
                               date_label=date_label,
                               goals=summary["goals"],
                               total_calories=summary["total_calories"],
                               total_protein=summary["total_protein"],
                               total_carbs=summary["total_carbs"],
                               total_fats=summary["total_fats"],
                               entry_count=len(summary["todays_entries"]))
    return app