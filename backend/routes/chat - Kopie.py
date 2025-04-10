from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from gpt4all import GPT4All
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import threading
import traceback

chat_bp = Blueprint("chat", __name__)

# Load GPT model
MODEL_PATH = os.getenv("MODEL_PATH", "C:/Users/Timur/AppData/Local/nomic.ai/GPT4All/qwen2.5-coder-7b-instruct-q4_0.gguf")
gpt_model = GPT4All(MODEL_PATH)

# Thread lock for model access
gpt_lock = threading.Lock()

# Load training chunks
try:
    with open("training_task_chunks.txt", "r", encoding="utf-8") as f:
        chunks = f.read().split("--- Chunk ")
        chunks = ["--- Chunk " + chunk.strip() for chunk in chunks if chunk.strip()]
except FileNotFoundError:
    chunks = []
    print("❌ training_task_chunks.txt not found!")

# Build embeddings if we have valid chunks
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
if chunks:
    embeddings = embedding_model.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))

def get_relevant_chunks(query, k=1):
    if not chunks:
        return []
    query_vec = embedding_model.encode([query])
    _, I = index.search(np.array(query_vec), k)
    return [chunks[i] for i in I[0]]

@chat_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    try:
        user_input = request.json.get("message", "").strip()
        if not user_input:
            return jsonify({"error": "Empty message received"}), 400

        context = "\n\n".join(get_relevant_chunks(user_input))
        prompt = (
            "You are a helpful AI chatbot that always responds in English. "
            "Use the following context to help answer the user's question.\n\n"
            f"{context}\n\nUser: {user_input}\nChatbot:"
        )

        with gpt_lock:
            response = gpt_model.generate(prompt, max_tokens=100, temp=0.7, top_k=40, top_p=0.9)

        return jsonify({"response": response.strip()})
    
    except Exception as e:
        print("❌ Chat Error:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
