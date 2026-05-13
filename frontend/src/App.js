import { useState, useRef } from "react";

const API = "http://127.0.0.1:8000";

export default function App() {
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi! Upload your notes and ask me anything about them." }
  ]);
  const [question, setQuestion] = useState("");
  const [uploadStatus, setUploadStatus] = useState("No file uploaded yet");
  const [loading, setLoading] = useState(false);
  const fileRef = useRef();
  const chatRef = useRef();

  const uploadPDF = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploadStatus("Uploading...");
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API}/upload`, { method: "POST", body: formData });
    const data = await res.json();
    setUploadStatus(data.message);
  };

  const askQuestion = async () => {
    if (!question.trim()) return;
    setMessages(prev => [...prev, { role: "user", text: question }]);
    setMessages(prev => [...prev, { role: "bot", text: "Thinking..." }]);
    setQuestion("");
    setLoading(true);
    const res = await fetch(`${API}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });
    const data = await res.json();
    setMessages(prev => [...prev.slice(0, -1), { role: "bot", text: data.answer }]);
    setLoading(false);
    setTimeout(() => chatRef.current?.scrollTo(0, chatRef.current.scrollHeight), 100);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-2xl flex flex-col gap-4">

        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-blue-400">📚 StudyMind</h1>
          <p className="text-gray-400 mt-1">Upload your notes and ask anything</p>
        </div>

        {/* Upload Box */}
        <div className="border-2 border-dashed border-blue-500 rounded-xl p-6 text-center bg-gray-900">
          <input type="file" accept=".pdf" ref={fileRef} onChange={uploadPDF} className="hidden" />
          <button
            onClick={() => fileRef.current.click()}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg font-medium transition"
          >
            📄 Upload PDF
          </button>
          <p className="text-blue-400 text-sm mt-3">{uploadStatus}</p>
        </div>

        {/* Chat Box */}
        <div ref={chatRef} className="bg-gray-900 rounded-xl p-4 h-80 overflow-y-auto flex flex-col gap-3">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`px-4 py-2 rounded-xl max-w-xs md:max-w-md text-sm leading-relaxed ${
                msg.role === "user" ? "bg-blue-500 text-white" : "bg-gray-800 text-gray-100"
              }`}>
                {msg.text}
              </div>
            </div>
          ))}
        </div>

        {/* Input Row */}
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === "Enter" && askQuestion()}
            placeholder="Ask a question about your notes..."
            className="flex-1 bg-gray-900 text-white px-4 py-3 rounded-xl outline-none border border-gray-700 focus:border-blue-500 transition"
          />
          <button
            onClick={askQuestion}
            disabled={loading}
            className="bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white px-6 py-3 rounded-xl font-medium transition"
          >
            Ask
          </button>
        </div>

      </div>
    </div>
  );
}