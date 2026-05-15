from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import json
import numpy as np
import pdfplumber
import tempfile
import os
import requests
import time
from groq import Groq
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

HF_KEY = os.getenv("HF_KEY")
GROQ_KEY = os.getenv("GROQ_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

groq_client = Groq(api_key=GROQ_KEY)

HF_EMBED_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
HF_HEADERS = {"Authorization": f"Bearer {HF_KEY}"}

def get_embedding(text: str):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.post(
                HF_EMBED_URL,
                headers=HF_HEADERS,
                json={"inputs": text, "options": {"wait_for_model": True}},
                timeout=60
            )

            print(f"HF attempt {attempt+1}: status={response.status_code}, body={response.text[:200]}")

            if response.status_code in [503, 500]:
                time.sleep(15)
                continue

            if not response.text.strip():
                time.sleep(15)
                continue

            result = response.json()

            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], float):
                    return result
                if isinstance(result[0], list) and len(result[0]) > 0:
                    return result[0]

            time.sleep(5)

        except Exception as e:
            print(f"HF exception attempt {attempt+1}: {e}")
            time.sleep(15)
            continue

    raise ValueError("HuggingFace model failed to respond after retries")

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
        embedding = get_embedding(chunk)
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

    question_embedding = np.array(get_embedding(question))

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

    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return {"answer": response.choices[0].message.content}


# -----------------------------
# ROUTE 3 - Health Check
# -----------------------------
@app.get("/")
def root():
    return {"status": "StudyMind API is running"}