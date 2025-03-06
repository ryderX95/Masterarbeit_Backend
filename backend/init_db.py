from database.database import db
from server import app

# Ensure database tables are created
with app.app_context():
    db.create_all()
    print("✅ Database created successfully!")
