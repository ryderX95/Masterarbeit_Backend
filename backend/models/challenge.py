from database.database import db
from models.user import UserProgress


class ChallengeProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, default=False)
