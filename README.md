# 📚 StudyMind — AI Teaching Assistant

An AI-powered RAG (Retrieval Augmented Generation) teaching assistant that lets you upload any PDF and ask questions in plain English. Built from scratch in 2 days.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green)
![React](https://img.shields.io/badge/React-18-61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue)
![Gemini](https://img.shields.io/badge/Gemini_API-2.0-orange)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-3.0-38BDF8)

---

## 🚀 What it does

Upload any PDF — lecture notes, textbooks, research papers — and ask questions about it in plain English. StudyMind finds the most relevant sections and gives you a clear, accurate answer drawn directly from your document.

**Example:**
- Upload your Data Science notes
- Ask "What is the difference between supervised and unsupervised learning?"
- Get a precise answer drawn directly from your notes

---

## 🖥️ Preview

> Dark glassmorphism UI with animated background, chat bubbles, PDF upload, and real-time AI answers.

---

## 🧠 How it works (RAG Pipeline)
User uploads PDF
↓
Text extracted using pdfplumber
↓
Text split into 500-word chunks
↓
Each chunk converted to vector embedding (Gemini API)
↓
Embeddings stored in PostgreSQL
↓
User asks a question
↓
Question converted to embedding
↓
Most relevant chunk found via cosine similarity
↓
Chunk + question sent to Gemini LLM
↓
Clear answer returned to chat UI

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js, Tailwind CSS, Glassmorphism UI |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| AI Embeddings | Google Gemini API (gemini-embedding-001) |
| AI Generation | Google Gemini API (gemini-2.5-flash-lite) |
| PDF Processing | pdfplumber |
| Vector Search | Cosine Similarity (NumPy) |

---

## ⚙️ Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/anshhh1101/studymind.git
cd studymind
```

### 2. Install backend dependencies
```bash
pip install fastapi uvicorn python-multipart pdfplumber psycopg2-binary google-genai numpy python-dotenv
```

### 3. Set up PostgreSQL
- Install PostgreSQL
- Create a database called `studymind`
- Run this in pgAdmin Query Tool:
```sql
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    chunk_text TEXT,
    embedding JSONB
);
```

### 4. Create .env file
GEMINI_KEY=your-gemini-api-key
DB_PASSWORD=your-postgresql-password

### 5. Run the backend
```bash
uvicorn main:app --reload
```

### 6. Run the frontend
```bash
cd frontend
npm install
npm start
```

### 7. Open in browser
Go to **http://localhost:3000**

---

## 📁 Project Structure
studymind/
├── main.py              # FastAPI backend (upload + ask endpoints)
├── frontend/
│   ├── src/
│   │   ├── App.js       # React frontend with Tailwind UI
│   │   └── index.css    # Tailwind directives
│   ├── package.json
│   └── tailwind.config.js
├── index.html           # Original HTML version
├── .env                 # API keys (not committed)
├── .gitignore
└── README.md

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Health check |
| POST | /upload | Upload and process a PDF |
| POST | /ask | Ask a question, get an answer |

---

## 🔮 Future Improvements

- [ ] Replace cosine similarity with pgvector for faster search
- [ ] Support multiple PDFs simultaneously
- [ ] Add chat history and memory
- [ ] Auto-generate quiz from uploaded notes
- [ ] User authentication with JWT
- [ ] Deploy to AWS (S3 + Lambda + RDS)
- [ ] Next.js migration for SSR

---

## 👨‍💻 Author

**Anshuman Dev**
B.Tech CSE, KIIT University | 2027 Batch
GitHub: [anshhh1101](https://github.com/anshhh1101)