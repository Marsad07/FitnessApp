from app import db
from datetime import datetime

class FoodCache(db.Model):
    __tablename__ = 'food_cache'
    id = db.Column(db.Integer, primary_key=True)
    search_term = db.Column(db.String(255), unique=True, nullable=False)
    results = db.Column(db.Text, nullable=False)
    cached_at = db.Column(db.DateTime, default=datetime.now)