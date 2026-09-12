from app import db

class FoodCache(db.Model):
    __tablename__ = 'food_cache'
    id = db.Column(db.Integer, primary_key=True)
    search_term = db.Column(db.String, unique=True)
    results = db.Column(db.String(500))
    cached_at = db.Column(db.DateTime)