from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from database.database import db
from config.config import Config
from routes.auth import auth_bp
from routes.challenges import challenges_bp
from routes.chat import chat_bp
from sqlalchemy import inspect
from flask_migrate import Migrate
from gpt4all import GPT4All  # Import local model


MODEL_PATH = os.getenv("MODEL_PATH", "C:/Users/Timur/.cache/gpt4all/gpt4all-falcon.Q4_0.gguf")


app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
jwt = JWTManager(app)
db.init_app(app)
migrate = Migrate(app, db)  # 👈 Add this after initializing the app

# ✅ Create Tables Before First Request
@app.before_request
def before_request():
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table("user"):
            db.create_all()
            print("✅ Database initialized!")

# ✅ Register Routes
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(challenges_bp, url_prefix="/challenges")

# ✅ Protected Chat Route (Mock Response)
@app.route("/chat", methods=["POST"])
@jwt_required()  # 🔒 Require authentication
def chat():
    user = get_jwt_identity()  # ✅ Get user from JWT
    user_input = request.json.get("message")

    if not user_input:
        return jsonify({"response": "Please enter a message."}), 400

    print(f"📥 {user} said: {user_input}")

    # Simulated response (GPT-4All will be added later)
    response = "This is a placeholder response from the chatbot."

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
