import { useState, useRef, useEffect } from "react";

const API = "https://studymind-jqmn.onrender.com";

export default function App() {
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi! Upload your notes and ask me anything about them." }
  ]);

  const [question, setQuestion] = useState("");
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState(null);

  const fileRef = useRef();
  const chatRef = useRef();

  useEffect(() => {
    chatRef.current?.scrollTo({
      top: chatRef.current.scrollHeight,
      behavior: "smooth"
    });
  }, [messages]);

  const uploadPDF = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setFileName(file.name);
    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      await fetch(`${API}/upload`, {
        method: "POST",
        body: formData
      });

      setMessages(prev => [
        ...prev,
        {
          role: "bot",
          text: `✅ "${file.name}" uploaded! Ask me anything about it.`
        }
      ]);
    } catch {
      setMessages(prev => [
        ...prev,
        {
          role: "bot",
          text: "❌ Failed to upload PDF."
        }
      ]);
    }

    setUploading(false);
  };

  const askQuestion = async () => {
    if (!question.trim() || loading) return;

    const q = question;

    setMessages(prev => [
      ...prev,
      { role: "user", text: q },
      { role: "bot", text: "...", loading: true }
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const res = await fetch(`${API}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: q })
      });

      const data = await res.json();

      setMessages(prev => [
        ...prev.slice(0, -1),
        { role: "bot", text: data.answer }
      ]);
    } catch {
      setMessages(prev => [
        ...prev.slice(0, -1),
        { role: "bot", text: "❌ Error connecting to backend." }
      ]);
    }

    setLoading(false);
  };

  return (
    <div
      className="min-h-screen text-white flex flex-col items-center justify-center p-4 font-sans"
      style={{ background: "#08080f" }}
    >
      {/* Background */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `
              radial-gradient(ellipse at 20% 50%, rgba(120,40,200,0.08) 0%, transparent 60%),
              radial-gradient(ellipse at 80% 20%, rgba(40,100,255,0.08) 0%, transparent 60%),
              radial-gradient(ellipse at 60% 80%, rgba(0,200,180,0.05) 0%, transparent 60%)
            `
          }}
        />

        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage:
              "linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)",
            backgroundSize: "40px 40px"
          }}
        />
      </div>

      <div className="w-full max-w-2xl flex flex-col gap-5 relative z-10">

        {/* Header */}
        <div className="text-center mb-2">
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs px-3 py-1 rounded-full mb-3">
            <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse"></span>
            AI Teaching Assistant
          </div>

          <h1 className="text-5xl font-bold tracking-tight">
            <span className="bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
              Study
            </span>

            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Mind
            </span>
          </h1>

          <p className="text-gray-500 text-sm mt-2">
            Upload your notes · Ask anything · Get instant answers
          </p>
        </div>

        {/* Upload Box */}
        <div
          onClick={() => fileRef.current.click()}
          className="cursor-pointer group border border-white/5 hover:border-blue-500/30 rounded-2xl p-6 text-center transition-all duration-300"
          style={{
            background: "rgba(255,255,255,0.03)",
            backdropFilter: "blur(10px)"
          }}
        >
          <input
            type="file"
            accept=".pdf"
            ref={fileRef}
            onChange={uploadPDF}
            className="hidden"
          />

          <div className="flex flex-col items-center gap-3">

            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-white/10 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
              📄
            </div>

            {uploading ? (
              <div className="flex items-center gap-2 text-blue-400 text-sm">
                <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />

                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v8z"
                  />
                </svg>

                Processing PDF...
              </div>
            ) : fileName ? (
              <div className="text-sm">
                <span className="text-green-400 font-medium">
                  {fileName}
                </span>

                <span className="text-gray-600 ml-2">
                  · Click to replace
                </span>
              </div>
            ) : (
              <div className="text-sm text-gray-500 group-hover:text-gray-400 transition-colors">
                <span className="text-blue-400 font-medium">
                  Click to upload
                </span>{" "}
                your PDF notes
              </div>
            )}
          </div>
        </div>

        {/* Chat Box */}
        <div
          ref={chatRef}
          className="rounded-2xl p-4 h-80 overflow-y-auto flex flex-col gap-3 border border-white/5"
          style={{
            background: "rgba(255,255,255,0.02)",
            backdropFilter: "blur(10px)"
          }}
        >
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex gap-2 ${
                msg.role === "user"
                  ? "justify-end"
                  : "justify-start"
              }`}
            >
              {msg.role === "bot" && (
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500/30 to-purple-500/30 border border-white/10 flex items-center justify-center text-xs flex-shrink-0 mt-0.5">
                  🤖
                </div>
              )}

              <div
                className={`px-4 py-2.5 rounded-2xl max-w-sm text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-tr-sm shadow-lg shadow-blue-500/20"
                    : "text-gray-300 rounded-tl-sm border border-white/5"
                }`}
                style={
                  msg.role === "bot"
                    ? { background: "rgba(255,255,255,0.05)" }
                    : {}
                }
              >
                {msg.loading ? (
                  <div className="flex gap-1 items-center h-4">
                    <span
                      className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0ms" }}
                    />

                    <span
                      className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    />

                    <span
                      className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    />
                  </div>
                ) : (
                  msg.text
                )}
              </div>

              {msg.role === "user" && (
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-xs flex-shrink-0 mt-0.5">
                  👤
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Input */}
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) =>
              e.key === "Enter" && askQuestion()
            }
            placeholder="Ask a question about your notes..."
            className="flex-1 text-white placeholder-gray-600 px-4 py-3 rounded-xl outline-none border border-white/5 focus:border-blue-500/40 transition-all text-sm"
            style={{
              background: "rgba(255,255,255,0.04)",
              backdropFilter: "blur(10px)"
            }}
          />

          <button
            onClick={askQuestion}
            disabled={loading || !question.trim()}
            className="bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-cyan-500 disabled:opacity-40 disabled:cursor-not-allowed text-white px-5 py-3 rounded-xl font-medium transition-all text-sm flex items-center gap-2 shadow-lg shadow-blue-500/20"
          >
            {loading ? (
              <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />

                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8v8z"
                />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
            )}

            Ask
          </button>
        </div>

        {/* Footer */}
        <p className="text-center text-gray-700 text-xs">
          Built by{" "}
          <span className="text-gray-500">
            Anshuman Dev
          </span>{" "}
          · RAG Pipeline · Gemini API · FastAPI · PostgreSQL
        </p>
      </div>
    </div>
  );
}