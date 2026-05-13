from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from google import genai
import psycopg2
import json
import numpy as np
import pdfplumber
import tempfile
import os

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your credentials
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_KEY")
DB_CONFIG = {
    "host": "localhost",
    "port": 5050,
    "database": "studymind",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD")
}

client = genai.Client(api_key=GEMINI_KEY)

def get_db():
    return psycopg2.connect(**DB_CONFIG)

# Route 1 - Upload PDF
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Extract text
    full_text = ""
    with pdfplumber.open(tmp_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    os.unlink(tmp_path)

    # Split into chunks
    words = full_text.split()
    chunk_size = 500
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    # Store in database
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM documents")  # Clear old documents
    for chunk in chunks:
        result = client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=chunk
        )
        embedding = result.embeddings[0].values
        cur.execute(
            "INSERT INTO documents (chunk_text, embedding) VALUES (%s, %s)",
            (chunk, json.dumps(embedding))
        )
    conn.commit()
    cur.close()
    conn.close()

    return {"message": f"PDF uploaded and processed. {len(chunks)} chunks stored."}

# Route 2 - Ask a question
@app.post("/ask")
async def ask_question(data: dict):
    question = data["question"]

    # Embed the question
    result = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=question
    )
    question_embedding = np.array(result.embeddings[0].values)

    # Find most relevant chunk
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT chunk_text, embedding FROM documents")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    best_score = -1
    best_chunk = ""
    for chunk_text, embedding_json in rows:
        chunk_embedding = np.array(embedding_json)
        similarity = np.dot(question_embedding, chunk_embedding) / (
            np.linalg.norm(question_embedding) * np.linalg.norm(chunk_embedding)
        )
        if similarity > best_score:
            best_score = similarity
            best_chunk = chunk_text

    # Get answer from Gemini
    prompt = f"""You are a helpful teaching assistant.
Answer the question based only on the context below.

Context:
{best_chunk}

Question: {question}

Answer clearly and concisely."""

    response = client.models.generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=prompt
    )

    return {"answer": response.text}

# Route 3 - Health check
@app.get("/")
def root():
    return {"status": "StudyMind API is running"}