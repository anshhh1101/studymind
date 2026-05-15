<div align="center">

# 🧠 StudyMind

### AI-Powered Teaching Assistant — RAG Pipeline

[![Live Demo](https://img.shields.io/badge/Live%20Demo-studymindv2--xi.vercel.app-blue?style=for-the-badge&logo=vercel)](https://studymindv2-xi.vercel.app)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://studymind-jqmn.onrender.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)

<br/>

> Upload your PDF notes · Ask anything · Get instant AI-powered answers

<br/>

![StudyMind Demo](https://via.placeholder.com/800x400/08080f/4A9EFF?text=StudyMind+—+AI+Teaching+Assistant)

</div>

---

## 📌 What is StudyMind?

**StudyMind** is a full-stack AI teaching assistant that lets students upload their PDF notes and ask natural language questions about them. It uses a **RAG (Retrieval-Augmented Generation)** pipeline to find the most relevant section of your notes and generate a precise, context-grounded answer — no hallucinations, no generic responses.

---

## ✨ Features

- 📄 **PDF Upload** — Upload any text-based PDF; text is extracted and chunked automatically
- 🔍 **Semantic Search** — Questions are matched to notes by meaning, not just keywords
- 🤖 **AI Answers** — LLaMA 3.3 70B (via Groq) generates clear, concise answers
- 💬 **Chat Interface** — Clean chat UI with message history and loading indicators
- ⚡ **Fast Inference** — Groq's LPU hardware delivers answers in seconds
- 🌐 **Fully Deployed** — Live on Vercel + Render, accessible from any device

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER                                  │
│                    (Browser / Mobile)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND — React + Tailwind CSS                 │
│                  Deployed on Vercel                          │
│         studymindv2-xi.vercel.app                           │
└───────────────────────┬─────────────────────────────────────┘
                        │  HTTP (REST API)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND — FastAPI + Python                      │
│                  Deployed on Render                          │
│         studymind-jqmn.onrender.com                         │
│                                                              │
│   POST /upload          POST /ask          GET /            │
│   ─────────────         ─────────          ──────           │
│   Extract text          Embed question     Health           │
│   Chunk (500w)          Cosine similarity  check            │
│   Embed chunks          Find best chunk                     │
│   Store in DB           Prompt LLaMA                        │
└──────┬────────────────────────┬────────────────────────────┘
       │                        │
       ▼                        ▼
┌──────────────┐      ┌─────────────────────────────────────┐
│  PostgreSQL  │      │         External APIs                │
│  (Render)    │      │                                      │
│              │      │  HuggingFace Inference API           │
│  chunks +    │      │  sentence-transformers/              │
│  embeddings  │      │  all-MiniLM-L6-v2                   │
│  (JSONB)     │      │  → 384-dim embeddings               │
└──────────────┘      │                                      │
                      │  Groq Cloud API                      │
                      │  llama-3.3-70b-versatile             │
                      │  → Answer generation                 │
                      └─────────────────────────────────────┘
```

---

## 🔬 How the RAG Pipeline Works

```
PDF Upload                          Question Asked
    │                                     │
    ▼                                     ▼
Extract Text                        Embed Question
(pdfplumber)                    (HuggingFace API)
    │                                     │
    ▼                                     ▼
Split into                          384-dim vector
500-word chunks                           │
    │                                     ▼
    ▼                             Cosine Similarity
Embed each chunk              vs all stored embeddings
(HuggingFace API)                         │
    │                                     ▼
    ▼                             Best matching chunk
Store in PostgreSQL                       │
as JSONB                                  ▼
                               Prompt = chunk + question
                                          │
                                          ▼
                               Groq LLaMA 3.3 70B
                                          │
                                          ▼
                                    Final Answer
```

---

## 🛠️ Tech Stack

<table>
  <thead>
    <tr>
      <th>Layer</th>
      <th>Technology</th>
      <th>Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Frontend</b></td>
      <td>React.js + Tailwind CSS</td>
      <td>Chat UI, PDF upload, state management</td>
    </tr>
    <tr>
      <td><b>Backend</b></td>
      <td>FastAPI (Python)</td>
      <td>REST API, PDF processing, RAG orchestration</td>
    </tr>
    <tr>
      <td><b>Embeddings</b></td>
      <td>HuggingFace — all-MiniLM-L6-v2</td>
      <td>384-dim semantic embeddings for chunks & queries</td>
    </tr>
    <tr>
      <td><b>LLM</b></td>
      <td>Groq — llama-3.3-70b-versatile</td>
      <td>Answer generation from retrieved context</td>
    </tr>
    <tr>
      <td><b>Database</b></td>
      <td>PostgreSQL 18</td>
      <td>Stores text chunks + embeddings as JSONB</td>
    </tr>
    <tr>
      <td><b>PDF Parsing</b></td>
      <td>pdfplumber</td>
      <td>Multi-page text extraction from PDF files</td>
    </tr>
    <tr>
      <td><b>Similarity</b></td>
      <td>NumPy cosine similarity</td>
      <td>Finds most relevant chunk for each question</td>
    </tr>
    <tr>
      <td><b>Frontend Deploy</b></td>
      <td>Vercel</td>
      <td>Auto-deploys React on every git push</td>
    </tr>
    <tr>
      <td><b>Backend Deploy</b></td>
      <td>Render</td>
      <td>Persistent Python web service + managed PostgreSQL</td>
    </tr>
  </tbody>
</table>

---

## 📁 Project Structure

```
studymind/
├── backend/
│   ├── main.py              # FastAPI app — all routes & RAG logic
│   └── requirements.txt     # Python dependencies
│
├── frontend/
│   └── src/
│       ├── App.jsx          # Main React component — full chat UI
│       ├── App.css          # Global styles
│       └── index.js         # React entry point
│
└── README.md
```

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (local or cloud)
- HuggingFace API key → [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- Groq API key → [console.groq.com](https://console.groq.com)

### Backend

```bash
# Clone the repo
git clone https://github.com/anshhh1101/studymind.git
cd studymind/backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "HF_KEY=your_huggingface_token" >> .env
echo "GROQ_KEY=your_groq_key" >> .env
echo "DATABASE_URL=postgresql://user:password@localhost/studymind" >> .env

# Run the server
uvicorn main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### Frontend

```bash
cd studymind/frontend

# Install dependencies
npm install

# Point to local backend (edit App.jsx line 3)
# const API = "http://localhost:8000";

# Start dev server
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## 🌍 Deployment

| Service | Platform | URL |
|---|---|---|
| Frontend | Vercel | [studymindv2-xi.vercel.app](https://studymindv2-xi.vercel.app) |
| Backend | Render | [studymind-jqmn.onrender.com](https://studymind-jqmn.onrender.com) |
| Database | Render PostgreSQL | Internal (Singapore region) |

### Environment Variables (Render)

| Key | Description |
|---|---|
| `HF_KEY` | HuggingFace API token (`hf_...`) |
| `GROQ_KEY` | Groq API key (`gsk_...`) |
| `DATABASE_URL` | Render internal PostgreSQL connection string |

---

## 📡 API Reference

### `GET /`
Health check
```json
{ "status": "StudyMind API is running" }
```

### `POST /upload`
Upload a PDF file
- **Body:** `multipart/form-data` with `file` field
- **Response:**
```json
{ "message": "PDF uploaded successfully. 6 chunks stored." }
```

### `POST /ask`
Ask a question about the uploaded PDF
- **Body:**
```json
{ "question": "What are the key features of the dashboard?" }
```
- **Response:**
```json
{ "answer": "The dashboard includes KPI cards, a sentiment slicer, a Bing Map..." }
```

---

## ⚠️ Known Limitations

- **Single document** — uploading a new PDF replaces the previous one
- **No conversation memory** — each question is independent
- **Free tier cold starts** — first request after inactivity may take ~50 seconds
- **No authentication** — app is publicly accessible

---

## 🔮 Future Improvements

- [ ] Top-k retrieval — use 3 best chunks instead of 1 for richer context
- [ ] Streaming responses — stream LLM output token by token
- [ ] Multi-document support — query across multiple uploaded PDFs
- [ ] Conversation history — maintain context across questions
- [ ] pgvector — replace JSONB with native vector similarity for scale
- [ ] User authentication — secure per-user document storage
- [ ] Mobile responsive improvements

---

## 👨‍💻 Author

**Anshuman Dev**
- GitHub: [@anshhh1101](https://github.com/anshhh1101)
- B.Tech | Roll No: 23051168

---

<div align="center">

Built with ❤️ using **RAG Pipeline · FastAPI · HuggingFace · Groq · PostgreSQL · React**

⭐ Star this repo if you found it useful!

</div>