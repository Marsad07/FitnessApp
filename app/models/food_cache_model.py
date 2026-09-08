from app import db
from sqlalchemy.dialects.mysql import MEDIUMTEXT

class FoodCache(db.Model):
    __tablename__ = 'food_cache'
    id = db.Column(db.Integer, primary_key=True)
    search_term = db.Column(db.String, unique=True)
    results = db.Column(db.MEDIUMTEXT)
    cached_at = db.Column(db.DateTime)