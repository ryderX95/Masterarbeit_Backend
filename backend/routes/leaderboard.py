from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from database.database import db
from models.user import User, UserProgress
from sqlalchemy import func

leaderboard_bp = Blueprint("leaderboard", __name__)

@leaderboard_bp.route("/leaderboard", methods=["GET"])
@jwt_required()
def get_leaderboard():
    """
    Fetch leaderboard rankings based on the number of correct answers.
    """
    leaderboard = (
        db.session.query(
            User.id, 
            User.username, 
            func.sum(UserProgress.correct_answers).label("total_correct_answers")
        )
        .join(UserProgress, User.id == UserProgress.user_id)
        .group_by(User.id, User.username)
        .order_by(func.sum(UserProgress.correct_answers).desc())
        .limit(10)  # Limit to top 10 users
        .all()
    )

    # Convert to list of dictionaries
    leaderboard_data = [
        {"user_id": user_id, "username": username, "correct_answers": total_correct_answers}
        for user_id, username, total_correct_answers in leaderboard
    ]

    return jsonify(leaderboard_data)
