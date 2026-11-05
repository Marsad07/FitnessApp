from app import db

class Nutrition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_accounts.id', ondelete='CASCADE'), nullable=False, unique=True)
    calories_goal = db.Column(db.DECIMAL(6,2))
    protein_goal = db.Column(db.DECIMAL(6,2))
    carbs_goal = db.Column(db.DECIMAL(6,2))
    fats_goal = db.Column(db.DECIMAL(6,2))

