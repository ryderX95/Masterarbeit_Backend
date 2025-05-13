from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

def save_progress(user_id, task_id, completed, correct_answers):
    from models.user import UserProgress, User
    print("save_progress called with:", user_id, task_id, completed, correct_answers)

    # Update or create progress entry
    progress = UserProgress.query.filter_by(user_id=user_id, task_id=task_id).first()
    if progress:
        progress.completed = completed
        progress.correct_answers = correct_answers
    else:
        progress = UserProgress(
            user_id=user_id,
            task_id=task_id,
            completed=completed,
            correct_answers=correct_answers
        )
        db.session.add(progress)

    total_points = db.session.query(
        db.func.sum(UserProgress.correct_answers)
    ).filter_by(user_id=user_id).scalar() or 0

    user = User.query.get(user_id)
    if user:
        user.points = total_points

    db.session.commit()



def get_progress(user_id):
    from models.user import UserProgress
    progress = UserProgress.query.filter_by(user_id=user_id).all()
    result = {p.task_id: {"completed": p.completed, "correct_answers": p.correct_answers} for p in progress}
    print("get_progress returning:", result)  
    return result


def init_models():
    from models.user import UserProgress 
    from models.challenge import ChallengeProgress  