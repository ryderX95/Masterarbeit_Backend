from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import save_progress, get_progress, db
from models.challenge import ChallengeProgress

challenges_bp = Blueprint("challenges", __name__)

# ✅ List of Available Challenges
@challenges_bp.route("/challenges", methods=["GET"])
@jwt_required()
def get_challenges():
    challenges = [
        {"id": "1", "title": "SQL Injection", "difficulty": "Medium"},
        {"id": "2", "title": "XSS Attack", "difficulty": "Easy"},
        {"id": "3", "title": "Broken Authentication", "difficulty": "Hard"},
    ]
    return jsonify(challenges)

# ✅ User Completes a Challenge
@challenges_bp.route("/challenges/complete", methods=["POST"])
@jwt_required()
def complete_challenge():
    data = request.json
    user_id = get_jwt_identity()  # ✅ `get_jwt_identity()` returns a string (the user ID)
    challenge_id = data.get("challenge_id")

    if not challenge_id:
        return jsonify({"message": "Challenge ID required"}), 400

    challenge = ChallengeProgress.query.filter_by(user_id=user_id, challenge_id=challenge_id).first()

    if challenge:
        return jsonify({"message": "Challenge already completed"}), 400

    new_challenge = ChallengeProgress(user_id=user_id, challenge_id=challenge_id, completed=True)
    db.session.add(new_challenge)
    db.session.commit()  # ✅ Commit the new challenge completion to the database

    return jsonify({"message": "Challenge completed!"}), 200

# ✅ Get User Progress
@challenges_bp.route("/progress", methods=["GET"])
@jwt_required()
def fetch_progress():
    user_id = get_jwt_identity()

    if not user_id:
        return jsonify({"error": "User ID required"}), 400

    progress = get_progress(user_id)
    return jsonify(progress)

# ✅ Store Progress When Answering a Question
@challenges_bp.route("/progress", methods=["POST"])
@jwt_required()
def update_progress():
    data = request.json
    user_id = get_jwt_identity()  # ✅ `get_jwt_identity()` returns a string
    task_id = data.get("task_id")
    answer = data.get("answer")

    if not task_id or answer is None:
        return jsonify({"error": "Missing task ID or answer"}), 400

    # ✅ Mock correct answers
    TASK_ANSWERS = {
       "AuthenticationEnumeration": "incorrect password",
        "BasicAuth": "base64 encoded credentials",
        "OSINT": "publicly available information",
        "PasswordReset": "email reset link",
        "VerboseErrors": "detailed error messages"
    }

    correct_answer = TASK_ANSWERS.get(task_id)
    formatted_user_answer = answer.strip().lower()  # ✅ Ensure it's defined before usage
    # ✅ Debugging Log
    print(f"🔍 Task ID: {task_id}")
    print(f"🔍 User Answer: '{formatted_user_answer}'")
    print(f"🔍 Correct Answer: '{correct_answer}'")

    is_correct = formatted_user_answer == correct_answer  # ✅ Compare normalized values

    # ✅ Save progress only if correct
    save_progress(user_id, task_id, completed=1 if is_correct else 0, correct_answers=1 if is_correct else 0)

    return jsonify({"correct": is_correct, "message": "Answer stored"})
