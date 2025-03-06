from database.database import db

class ChallengeProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, default=False)
