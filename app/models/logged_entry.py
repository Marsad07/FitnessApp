from app import db
from sqlalchemy.dialects.mysql import MEDIUMTEXT

class LoggedEntry(db.Model):
    __tablename__ = 'logged_entries'
    id = db.Column(db.Integer, primary_key=True)
    fdc_id = db.Column(db.Integer)
    food_name = db.Column(db.String(255))
    food_weight = db.Column(db.DECIMAL(6,2))
    calories = db.Column(db.DECIMAL(6,2))
    protein = db.Column(db.DECIMAL(6,2))
    carbs = db.Column(db.DECIMAL(6,2))
    fats = db.Column(db.DECIMAL(6,2))
    meal_category = db.Column(db.String(255))
    logged_at = db.Column(db.DateTime)

class FoodCache(db.Model):
    __tablename__ = 'food_cache'
    id = db.Column(db.Integer, primary_key=True)
    search_term = db.Column(db.String, unique=True)
    results = db.Column(db.MEDIUMTEXT)
    cached_at = db.Column(db.DateTime)