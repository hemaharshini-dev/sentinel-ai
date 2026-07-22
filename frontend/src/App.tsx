import { useState } from "react";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("");
  const [analysis, setAnalysis] = useState<any>(null);
  const [crisis, setCrisis] = useState<any>(null);

  const analyze = async () => {
    const response = await axios.post("http://127.0.0.1:8000/analyze", {
      message,
    });

    setAnalysis(response.data);
    setCrisis(null);
  };

  const handleReply = async (reply: string) => {
    const response = await axios.post("http://127.0.0.1:8000/crisis", {
      analysis,
      user_reply: reply,
    });

    setCrisis(response.data);
  };

  return (
    <div style={{ maxWidth: "900px", margin: "40px auto" }}>
      <h1>🛡️ Sentinel AI</h1>

      <textarea
        rows={10}
        style={{ width: "100%", padding: "10px" }}
        placeholder="Paste suspicious message..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />

      <br />
      <br />

      <button onClick={analyze}>Analyze</button>

      <br />
      <br />

      {analysis && (
        <div>
          <h2>Scam Type</h2>
          <p>{analysis.scam_type}</p>

          <h2>Summary</h2>
          <p>{analysis.summary}</p>

          <h2>Reason</h2>
          <p>{analysis.reason}</p>

          <h2>Immediate Actions</h2>

          <ul>
            {analysis.immediate_actions?.map(
              (action: string, index: number) => (
                <li key={index}>{action}</li>
              ),
            )}
          </ul>

          <hr />

          <h2>🚨 Stay With Me</h2>

          <p>{analysis.next_question}</p>

          <div style={{ display: "flex", gap: "10px" }}>
            {analysis.options?.map((option: string) => (
              <button key={option} onClick={() => handleReply(option)}>
                {option}
              </button>
            ))}
          </div>
        </div>
      )}

      {crisis && (
        <div style={{ marginTop: "30px" }}>
          <hr />

          <h2>Sentinel AI</h2>

          <p>{crisis.message}</p>

          <h3>{crisis.next_question}</h3>

          <div style={{ display: "flex", gap: "10px" }}>
            {crisis.options?.map((option: string) => (
              <button key={option} onClick={() => handleReply(option)}>
                {option}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
