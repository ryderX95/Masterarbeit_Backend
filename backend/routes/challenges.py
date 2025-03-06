from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import db
from models.challenge import ChallengeProgress

challenges_bp = Blueprint("challenges", __name__)

@challenges_bp.route("/challenges", methods=["GET"])
@jwt_required()
def get_challenges():
    challenges = [
        {"id": "1", "title": "SQL Injection", "difficulty": "Medium"},
        {"id": "2", "title": "XSS Attack", "difficulty": "Easy"},
        {"id": "3", "title": "Broken Authentication", "difficulty": "Hard"},
    ]
    return jsonify(challenges)

@challenges_bp.route("/challenges/complete", methods=["POST"])
@jwt_required()
def complete_challenge():
    data = request.json
    user_id = get_jwt_identity()["id"]
    challenge_id = data.get("challenge_id")

    if not challenge_id:
        return jsonify({"message": "Challenge ID required"}), 400

    challenge = ChallengeProgress.query.filter_by(user_id=user_id, challenge_id=challenge_id).first()

    if challenge:
        return jsonify({"message": "Challenge already completed"}), 400

    new_challenge = ChallengeProgress(user_id=user_id, challenge_id=challenge_id, completed=True)
    db.session.add(new_challenge)
    
    return jsonify({"message": "Challenge completed!"}), 200
