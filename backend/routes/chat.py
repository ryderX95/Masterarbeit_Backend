from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import requests
import traceback
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

chat_bp = Blueprint("chat", __name__)

# LLaMA server endpoint
LLAMA_SERVER_URL = "http://127.0.0.1:8001/completion"

# Load embedding model once
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load training chunks from file
try:
    with open("training_task_chunks.txt", "r", encoding="utf-8") as f:
        raw_chunks = f.read().split("--- Chunk ")
        chunks = ["--- Chunk " + chunk.strip() for chunk in raw_chunks if chunk.strip()]
except FileNotFoundError:
    chunks = []
    print("❌ training_task_chunks.txt not found!")

# Prepare FAISS index
if chunks:
    embeddings = embedding_model.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))

def get_relevant_chunks(query, k=2):
    """Returns the top-k most relevant chunks for the query."""
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

        # Retrieve RAG context
        rag_context = "\n\n".join(get_relevant_chunks(user_input))

        # Format the prompt
        prompt = f"""### Instruction:
Answer the question using the provided context. Be **very concise** and to the point — use only the minimum necessary words.

### Context:
{rag_context}

### Question:
{user_input}

### Response:"""

        # Send to LLaMA server
        res = requests.post(LLAMA_SERVER_URL, json={
            "prompt": prompt,
            "n_predict": 40,
            "temperature": 0.3,
            "top_k": 20,
            "top_p": 0.85,
            "stop": ["### Question:", "### Instruction:", "### Response:"]
        })

        if res.ok:
            return jsonify({"response": res.json().get("content", "").strip()})
        else:
            return jsonify({"error": f"LLM server error: {res.status_code}"}), 500

    except Exception as e:
        print("❌ Chat Error:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
