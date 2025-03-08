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
    try:
        user_input = request.json.get("message", "").strip()

        if not user_input:
            return jsonify({"error": "Empty message received"}), 400

        # Ensure chatbot responds concisely in English
        prompt = (
            "You are a helpful AI chatbot that always responds in English. "
            "Keep responses concise and clear. "
            f"User: {user_input}\n"
            "Chatbot:"
        )

        response = gpt_model.generate(prompt, max_tokens=100)  # Limiting response length

        return jsonify({"response": response.strip()})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
