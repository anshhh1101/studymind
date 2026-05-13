# StudyMind — AI Teaching Assistant (RAG Pipeline)

A RAG-based teaching assistant that lets you upload any PDF and ask questions in plain English.

## How it works
1. Upload a PDF (lecture notes, textbook, anything)
2. Text is extracted and split into chunks
3. Chunks are converted to vector embeddings using Gemini API
4. Embeddings stored in PostgreSQL
5. Ask a question → system finds relevant chunks → Gemini answers

## Tech Stack
- Python, pdfplumber, psycopg2
- Google Gemini API (embeddings + generation)
- PostgreSQL (vector storage)

## Author
Anshuman Dev | github.com/anshhh1101