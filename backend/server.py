import os  # ✅ Fix the missing import
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from database.database import db, init_models
from config.config import Config
from routes.auth import auth_bp
from routes.challenges import challenges_bp
from routes.chat import chat_bp
from sqlalchemy import inspect
from flask_migrate import Migrate
from gpt4all import GPT4All  # ✅ Import GPT4All
from routes.leaderboard import leaderboard_bp  # ✅ Import leaderboard


app = Flask(__name__)

# Use your actual PostgreSQL URL here
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:miciamoluca@localhost:5432/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config.from_object(Config)
CORS(app)
jwt = JWTManager(app)
db.init_app(app)

# ✅ Initialize models inside app context
with app.app_context():
    init_models()
    db.create_all()  # ✅ Ensure all tables are created

migrate = Migrate(app, db)

# ✅ Load GPT4All Model (Disable CUDA to avoid errors)
MODEL_PATH = os.getenv("MODEL_PATH", "C:/Users/Timur/AppData/Local/nomic.ai/GPT4All/qwen2.5-coder-7b-instruct-q4_0.gguf")

try:
    gpt_model = GPT4All(MODEL_PATH, allow_download=False, device="cpu")  # ✅ Force CPU mode
except Exception as e:
    print(f"⚠️ Failed to load GPT4All model: {e}")
    gpt_model = None

# ✅ Register Routes
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(challenges_bp, url_prefix="/challenges")
app.register_blueprint(leaderboard_bp, url_prefix="/leaderboard")  # ✅ Register leaderboard API


# ✅ Protected Chat Route
@app.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    user = get_jwt_identity()
    user_input = request.json.get("message")

    if not user_input:
        return jsonify({"response": "Please enter a message."}), 400

    print(f"📥 {user} said: {user_input}")

    if gpt_model:
        try:
            chatbot_response = gpt_model.generate(user_input)
        except Exception as e:
            print(f"⚠️ GPT4All Error: {e}")
            chatbot_response = "Error generating response."
    else:
        chatbot_response = "GPT4All model is not loaded."

    return jsonify({"response": chatbot_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
