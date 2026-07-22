import { useState } from "react";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("");
  const [result, setResult] = useState<any>(null);

  const analyze = async () => {
    const response = await axios.post("http://127.0.0.1:8000/analyze", {
      message,
    });

    setResult(response.data);
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

      {result && (
        <div>
          <h2>Scam Type</h2>
          <p>{result.scam_type}</p>

          <h2>Summary</h2>
          <p>{result.summary}</p>

          <h2>Reason</h2>
          <p>{result.reason}</p>

          <h2>Immediate Actions</h2>

          <ul>
            {result.immediate_actions.map((action: string, index: number) => (
              <li key={index}>{action}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
