import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from config.config import Config
from database.database import db, init_models
from routes.auth import auth_bp
from routes.challenges import challenges_bp
from routes.chat import chat_bp
from routes.leaderboard import leaderboard_bp

app = Flask(__name__)

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:miciamoluca@localhost:5432/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config.from_object(Config)

# CORS & JWT
CORS(app, origins="http://localhost:5173", methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])
jwt = JWTManager(app)

# Database setup
db.init_app(app)
with app.app_context():
    init_models()
    db.create_all()

migrate = Migrate(app, db)

# Routes
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(challenges_bp, url_prefix="/challenges")
app.register_blueprint(leaderboard_bp, url_prefix="")
app.register_blueprint(chat_bp, url_prefix="") 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
