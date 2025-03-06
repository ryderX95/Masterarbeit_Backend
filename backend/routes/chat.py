from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from gpt4all import GPT4All
import os

chat_bp = Blueprint("chat", __name__)

# Load Model (Ensure this path is correct)
MODEL_PATH = os.getenv("MODEL_PATH", "C:/Users/Timur/AppData/Local/nomic.ai/GPT4All/qwen2.5-coder-7b-instruct-q4_0.gguf")
gpt_model = GPT4All(MODEL_PATH)

@chat_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"response": "Please enter a message."}), 400

    # Generate response
    response = gpt_model.generate(user_input)
    return jsonify({"response": response})
