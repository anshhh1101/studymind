from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
import psycopg2
import json
import numpy as np
import pdfplumber
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_KEY = os.getenv("GEMINI_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

client = genai.Client(api_key=GEMINI_KEY)

def get_db():
    return psycopg2.connect(DATABASE_URL)

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

# -----------------------------
# ROUTE 1 - Upload PDF
# -----------------------------
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    full_text = ""
    with pdfplumber.open(tmp_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    os.unlink(tmp_path)

    if not full_text.strip():
        return {"message": "Could not extract text from PDF."}

    words = full_text.split()
    chunk_size = 500
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM documents")

    for chunk in chunks:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=chunk,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )
        embedding = result.embeddings[0].values

        cur.execute(
            "INSERT INTO documents (chunk_text, embedding) VALUES (%s, %s)",
            (chunk, json.dumps(embedding))
        )

    conn.commit()
    cur.close()
    conn.close()

    return {"message": f"PDF uploaded successfully. {len(chunks)} chunks stored."}


# -----------------------------
# ROUTE 2 - Ask Question
# -----------------------------
@app.post("/ask")
async def ask_question(data: dict):

    question = data.get("question", "").strip()
    if not question:
        return {"answer": "Please ask a valid question."}

    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=question,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
    )
    question_embedding = np.array(result.embeddings[0].values)

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT chunk_text, embedding FROM documents")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return {"answer": "No documents found. Please upload a PDF first."}

    best_score = -1
    best_chunk = ""

    for chunk_text, embedding_json in rows:
        if isinstance(embedding_json, str):
            embedding_json = json.loads(embedding_json)
        chunk_embedding = np.array(embedding_json)

        similarity = np.dot(question_embedding, chunk_embedding) / (
            np.linalg.norm(question_embedding) * np.linalg.norm(chunk_embedding)
        )

        if similarity > best_score:
            best_score = similarity
            best_chunk = chunk_text

    prompt = f"""You are a helpful teaching assistant.

Answer the question based ONLY on the context below.

Context:
{best_chunk}

Question:
{question}

Answer clearly and concisely."""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return {"answer": response.text}


# -----------------------------
# ROUTE 3 - Health Check
# -----------------------------
@app.get("/")
def root():
    return {"status": "StudyMind API is running"}