import os
from flask import Flask, render_template
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

    @app.route('/')
    def homepage():
        return render_template('/online/homepage/homepage.html')

    return app
