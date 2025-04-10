from database.database import db
from server import app

with app.app_context():
    db.create_all()
    print("Database created successfully!")
