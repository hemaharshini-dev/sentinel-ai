import { useState } from "react";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("");
  const [result, setResult] = useState("");

  const analyze = async () => {
    const response = await axios.post("http://127.0.0.1:8000/analyze", {
      message,
    });

    setResult(response.data.summary);
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

      <h2>{result}</h2>
    </div>
  );
}

export default App;
