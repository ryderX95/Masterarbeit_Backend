from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

def save_progress(user_id, task_id, completed, correct_answers):
    from models.user import UserProgress  # ✅ Ensure UserProgress is imported
    progress = UserProgress.query.filter_by(user_id=user_id, task_id=task_id).first()
    if progress:
        progress.completed = completed
        progress.correct_answers = correct_answers
    else:
        progress = UserProgress(user_id=user_id, task_id=task_id, completed=completed, correct_answers=correct_answers)
        db.session.add(progress)

    db.session.commit()

def get_progress(user_id):
    from models.user import UserProgress  # ✅ Ensure UserProgress is imported
    progress = UserProgress.query.filter_by(user_id=user_id).all()
    return {p.task_id: {"completed": p.completed, "correct_answers": p.correct_answers} for p in progress}

def init_models():
    from models.user import UserProgress  # ✅ Delayed import
    from models.challenge import ChallengeProgress  # ✅ Import ChallengeProgress if needed