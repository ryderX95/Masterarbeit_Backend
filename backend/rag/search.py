from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import json

# Load text chunks (generated from training)
with open("training_task_chunks.txt", "r", encoding="utf-8") as f:
    chunks = f.read().split("--- Chunk ")[1:]
    chunks = ["--- Chunk " + chunk.strip() for chunk in chunks if chunk.strip()]

# Load embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")

# Build FAISS index
embeddings = model.encode(chunks)
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings))

def get_relevant_chunks(query, k=3):
    query_vec = model.encode([query])
    _, I = index.search(np.array(query_vec), k)
    return [chunks[i] for i in I[0]]
