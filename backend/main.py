from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import psycopg2
import json
import numpy as np
import pdfplumber
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
GEMINI_KEY = os.getenv("GEMINI_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)

# Gemini models
chat_model = genai.GenerativeModel("gemini-1.5-flash")
embedding_model = "models/text-embedding-004"

# PostgreSQL connection
def get_db():
    return psycopg2.connect(DATABASE_URL)

# Initialize database table
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            chunk_text TEXT,
            embedding JSONB
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

init_db()

# Route 1 - Upload PDF
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # Save uploaded PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Extract text from PDF
    full_text = ""

    with pdfplumber.open(tmp_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if text:
                full_text += text + "\n"

    os.unlink(tmp_path)

    # Split text into chunks
    words = full_text.split()
    chunk_size = 500
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    # Store embeddings in database
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM documents")

    for chunk in chunks:

        result = genai.embed_content(
            model=embedding_model,
            content=chunk
        )

        embedding = result["embedding"]

        cur.execute(
            "INSERT INTO documents (chunk_text, embedding) VALUES (%s, %s)",
            (chunk, json.dumps(embedding))
        )

    conn.commit()
    cur.close()
    conn.close()

    return {
        "message": f"PDF uploaded and processed. {len(chunks)} chunks stored."
    }

# Route 2 - Ask Question
@app.post("/ask")
async def ask_question(data: dict):

    question = data["question"]

    # Create question embedding
    result = genai.embed_content(
        model=embedding_model,
        content=question
    )

    question_embedding = np.array(result["embedding"])

    # Fetch stored chunks
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT chunk_text, embedding FROM documents")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    # Find most similar chunk
    best_score = -1
    best_chunk = ""

    for chunk_text, embedding_json in rows:

        chunk_embedding = np.array(json.loads(embedding_json))

        similarity = np.dot(question_embedding, chunk_embedding) / (
            np.linalg.norm(question_embedding) *
            np.linalg.norm(chunk_embedding)
        )

        if similarity > best_score:
            best_score = similarity
            best_chunk = chunk_text

    # Prompt Gemini
    prompt = f"""
You are a helpful teaching assistant.

Answer the question based only on the context below.

Context:
{best_chunk}

Question:
{question}

Answer clearly and concisely.
"""

    response = chat_model.generate_content(prompt)

    return {
        "answer": response.text
    }

# Route 3 - Health Check
@app.get("/")
def root():
    return {
        "status": "StudyMind API is running"
    }