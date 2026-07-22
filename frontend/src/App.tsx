import { useState } from "react";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("");
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    if (!message.trim()) {
      alert("Please enter a suspicious message.");
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post("http://127.0.0.1:8000/analyze", {
        message,
      });

      setAnalysis(response.data);
    } catch (error) {
      console.error(error);
      alert("Something went wrong while analyzing.");
    } finally {
      setLoading(false);
    }
  };

  const cardStyle = {
    border: "1px solid #ccc",
    borderRadius: "10px",
    padding: "20px",
    marginBottom: "20px",
    background: "#1e1e1e",
  };

  const preStyle = {
    whiteSpace: "pre-wrap" as const,
    wordBreak: "break-word" as const,
    overflowX: "auto" as const,
    fontSize: "14px",
    lineHeight: "1.5",
  };

  return (
    <div
      style={{
        maxWidth: "1000px",
        margin: "40px auto",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1>🛡️ Sentinel AI</h1>
      <h3>AI Powered Fraud Network Intelligence Platform</h3>

      <textarea
        rows={10}
        style={{
          width: "100%",
          padding: "12px",
          fontSize: "15px",
          borderRadius: "8px",
        }}
        placeholder="Paste a suspicious message or complaint..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />

      <br />
      <br />

      <button
        onClick={analyze}
        disabled={loading}
        style={{
          padding: "10px 25px",
          cursor: loading ? "not-allowed" : "pointer",
          fontSize: "16px",
          borderRadius: "6px",
        }}
      >
        {loading ? "Analyzing..." : "Analyze Complaint"}
      </button>

      <br />
      <br />

      {analysis && (
        <>
          {/* Investigation */}
          <div style={cardStyle}>
            <h2>🕵️ Investigation</h2>

            <p>
              <strong>Scam Type:</strong> {analysis.investigation?.scam_type}
            </p>

            <p>
              <strong>Summary:</strong> {analysis.investigation?.summary}
            </p>

            <p>
              <strong>Reason:</strong> {analysis.investigation?.reason}
            </p>

            <strong>Immediate Actions</strong>

            <ul>
              {analysis.investigation?.immediate_actions?.map(
                (action: string, index: number) => (
                  <li key={index}>{action}</li>
                ),
              )}
            </ul>
          </div>

          <hr />

          {/* Entities */}
          <div style={cardStyle}>
            <h2>📞 Extracted Entities</h2>

            <pre style={preStyle}>
              {analysis.entities
                ? JSON.stringify(analysis.entities, null, 2)
                : "No entities found"}
            </pre>
          </div>

          <hr />

          {/* Intelligence */}
          <div style={cardStyle}>
            <h2>🕸 Fraud Intelligence</h2>

            <pre style={preStyle}>
              {analysis.intelligence
                ? JSON.stringify(analysis.intelligence, null, 2)
                : "No intelligence available"}
            </pre>
          </div>

          <hr />

          {/* Report */}
          <div style={cardStyle}>
            <h2>📄 Intelligence Report</h2>

            <pre style={preStyle}>
              {analysis.report
                ? JSON.stringify(analysis.report, null, 2)
                : "No report generated"}
            </pre>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
