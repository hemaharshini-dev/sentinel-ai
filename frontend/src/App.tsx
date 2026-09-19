import { useState, useRef, useEffect } from "react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

// ── Severity colours for the risk badge ──────────────────────────────────────
const SEVERITY_COLORS: Record<string, { bg: string; text: string }> = {
  LOW:      { bg: "#166534", text: "#bbf7d0" },
  MEDIUM:   { bg: "#854d0e", text: "#fef08a" },
  HIGH:     { bg: "#9a3412", text: "#fed7aa" },
  CRITICAL: { bg: "#7f1d1d", text: "#fecaca" },
};

// ── Entity badge colours ──────────────────────────────────────────────────────
const ENTITY_COLORS: Record<string, string> = {
  phone_numbers:          "#2563eb",
  upi_ids:                "#059669",
  emails:                 "#d97706",
  urls:                   "#dc2626",
  telegram_ids:           "#7c3aed",
  government_authorities: "#4b5563",
  bank_accounts:          "#0891b2",
  amounts:                "#b45309",
};

// ── Small reusable components ─────────────────────────────────────────────────

function Card({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      border: "1px solid #2e2e3a",
      borderRadius: 12,
      padding: "20px 24px",
      marginBottom: 20,
      background: "#16171d",
    }}>
      {children}
    </div>
  );
}

function SectionTitle({ emoji, title }: { emoji: string; title: string }) {
  return (
    <h2 style={{ margin: "0 0 16px", fontSize: 18, color: "#f3f4f6", display: "flex", alignItems: "center", gap: 8 }}>
      <span>{emoji}</span> {title}
    </h2>
  );
}

function EntityBadge({ value, color }: { value: string; color: string }) {
  return (
    <span style={{
      background: color,
      color: "#fff",
      borderRadius: 6,
      padding: "3px 10px",
      fontSize: 13,
      margin: "3px 4px 3px 0",
      display: "inline-block",
      fontFamily: "monospace",
    }}>
      {value}
    </span>
  );
}

function RiskBadge({ score, severity }: { score: number; severity: string }) {
  const colors = SEVERITY_COLORS[severity] ?? SEVERITY_COLORS.LOW;
  return (
    <div style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 10,
      background: colors.bg,
      color: colors.text,
      borderRadius: 8,
      padding: "8px 16px",
      fontWeight: 600,
      fontSize: 15,
      marginBottom: 16,
    }}>
      <span style={{ fontSize: 22 }}>
        {severity === "CRITICAL" ? "🚨" : severity === "HIGH" ? "⚠️" : severity === "MEDIUM" ? "🔶" : "🟢"}
      </span>
      {severity} — {score}/100
    </div>
  );
}

function Skeleton() {
  return (
    <div style={{
      background: "#1f2028",
      borderRadius: 12,
      height: 120,
      marginBottom: 20,
      animation: "pulse 1.5s ease-in-out infinite",
    }} />
  );
}

// ── Crisis Companion chat ─────────────────────────────────────────────────────

interface CrisisMessage {
  role: "sentinel" | "user";
  text: string;
  options?: string[];
}

function CrisisCompanion({ analysis }: { analysis: any }) {
  const [messages, setMessages] = useState<CrisisMessage[]>([
    {
      role: "sentinel",
      text: "I'm here to help you through this. What would you like to know or do next?",
      options: ["What should I do right now?", "I already sent money", "How do I file a complaint?"],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text: string) => {
    if (!text.trim() || loading) return;
    const userText = text.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", text: userText }]);
    setLoading(true);

    try {
      const res = await axios.post(`${API_BASE}/crisis`, {
        analysis,
        user_reply: userText,
      });
      const data = res.data;
      setMessages(prev => [...prev, {
        role: "sentinel",
        text: data.message ?? "I'm here to help.",
        options: data.options ?? [],
      }]);
    } catch {
      setMessages(prev => [...prev, {
        role: "sentinel",
        text: "Sorry, I had trouble responding. Please try again.",
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <SectionTitle emoji="💬" title="Crisis Companion" />
      <p style={{ color: "#9ca3af", fontSize: 13, marginBottom: 16 }}>
        Context-aware support based on your complaint analysis.
      </p>

      {/* Message thread */}
      <div style={{
        background: "#0f1015",
        borderRadius: 8,
        padding: 16,
        maxHeight: 340,
        overflowY: "auto",
        marginBottom: 12,
      }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: 14 }}>
            <div style={{
              display: "flex",
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
            }}>
              <div style={{
                maxWidth: "80%",
                background: msg.role === "user" ? "#2563eb" : "#1f2028",
                color: "#f3f4f6",
                borderRadius: msg.role === "user" ? "12px 12px 2px 12px" : "12px 12px 12px 2px",
                padding: "10px 14px",
                fontSize: 14,
                lineHeight: 1.5,
              }}>
                {msg.role === "sentinel" && (
                  <span style={{ fontWeight: 600, color: "#c084fc", fontSize: 12, display: "block", marginBottom: 4 }}>
                    🛡️ Sentinel
                  </span>
                )}
                {msg.text}
              </div>
            </div>

            {/* Quick reply options */}
            {msg.role === "sentinel" && msg.options && msg.options.length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 8, paddingLeft: 4 }}>
                {msg.options.map((opt, j) => (
                  <button
                    key={j}
                    onClick={() => send(opt)}
                    disabled={loading}
                    style={{
                      background: "transparent",
                      border: "1px solid #4b5563",
                      color: "#d1d5db",
                      borderRadius: 16,
                      padding: "4px 12px",
                      fontSize: 13,
                      cursor: "pointer",
                    }}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{ color: "#6b7280", fontSize: 13, fontStyle: "italic" }}>
            Sentinel is typing...
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input row */}
      <div style={{ display: "flex", gap: 8 }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && send(input)}
          placeholder="Type a message or question..."
          disabled={loading}
          style={{
            flex: 1,
            padding: "10px 14px",
            borderRadius: 8,
            border: "1px solid #2e2e3a",
            background: "#0f1015",
            color: "#f3f4f6",
            fontSize: 14,
          }}
        />
        <button
          onClick={() => send(input)}
          disabled={loading || !input.trim()}
          style={{
            padding: "10px 18px",
            borderRadius: 8,
            background: "#7c3aed",
            color: "#fff",
            border: "none",
            cursor: loading || !input.trim() ? "not-allowed" : "pointer",
            fontSize: 14,
            fontWeight: 600,
          }}
        >
          Send
        </button>
      </div>
    </Card>
  );
}

// ── Main App ──────────────────────────────────────────────────────────────────

function App() {
  const [message, setMessage] = useState("");
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async () => {
    if (!message.trim()) {
      setError("Please enter a suspicious message.");
      return;
    }
    setError(null);
    setLoading(true);
    setAnalysis(null);

    try {
      const response = await axios.post(`${API_BASE}/analyze`, { message });
      setAnalysis(response.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Something went wrong. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const entities = analysis?.entities ?? {};

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", padding: "0 20px", fontFamily: "system-ui, sans-serif", color: "#d1d5db" }}>

      {/* Header */}
      <h1 style={{ color: "#f3f4f6", marginBottom: 4 }}>🛡️ Sentinel AI</h1>
      <p style={{ color: "#9ca3af", marginBottom: 28, fontSize: 15 }}>
        AI Powered Fraud Network Intelligence Platform
      </p>

      {/* Input */}
      <textarea
        rows={8}
        style={{
          width: "100%",
          padding: 14,
          fontSize: 15,
          borderRadius: 10,
          border: "1px solid #2e2e3a",
          background: "#0f1015",
          color: "#f3f4f6",
          boxSizing: "border-box",
          resize: "vertical",
        }}
        placeholder="Paste a suspicious message or complaint..."
        value={message}
        onChange={e => { setMessage(e.target.value); setError(null); }}
      />

      {error && (
        <p style={{ color: "#f87171", fontSize: 14, margin: "8px 0 0" }}>{error}</p>
      )}

      <button
        onClick={analyze}
        disabled={loading || !message.trim()}
        style={{
          marginTop: 14,
          padding: "11px 28px",
          fontSize: 15,
          fontWeight: 600,
          borderRadius: 8,
          background: loading ? "#374151" : "#7c3aed",
          color: "#fff",
          border: "none",
          cursor: loading || !message.trim() ? "not-allowed" : "pointer",
        }}
      >
        {loading ? "Analyzing..." : "Analyze Complaint"}
      </button>

      <div style={{ marginTop: 32 }}>

        {/* Loading skeletons */}
        {loading && <><Skeleton /><Skeleton /><Skeleton /></>}

        {analysis && (
          <>
            {/* Language banner — only shown if translated */}
            {analysis.language?.was_translated && (
              <div style={{
                background: "#1e3a5f",
                border: "1px solid #2563eb",
                borderRadius: 8,
                padding: "10px 16px",
                marginBottom: 20,
                fontSize: 14,
                color: "#bfdbfe",
              }}>
                🌐 Complaint detected in <strong>{analysis.language.original_language_name}</strong> — automatically translated to English for analysis.
              </div>
            )}

            {/* Risk Badge — shown prominently at the top */}
            {analysis.risk && (
              <Card>
                <SectionTitle emoji="⚡" title="Risk Assessment" />
                <RiskBadge
                  score={analysis.risk.risk_score}
                  severity={analysis.risk.severity}
                />
                {analysis.risk.risk_factors?.length > 0 && (
                  <ul style={{ margin: "12px 0 0", paddingLeft: 20, lineHeight: 1.8, color: "#d1d5db" }}>
                    {analysis.risk.risk_factors.map((f: string, i: number) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                )}
              </Card>
            )}

            {/* Investigation */}
            <Card>
              <SectionTitle emoji="🕵️" title="Investigation" />
              <p style={{ marginBottom: 8 }}>
                <span style={{ color: "#9ca3af", fontSize: 13 }}>Scam Type</span><br />
                <strong style={{ color: "#f3f4f6" }}>{analysis.investigation?.scam_type}</strong>
              </p>
              <p style={{ marginBottom: 8 }}>
                <span style={{ color: "#9ca3af", fontSize: 13 }}>Summary</span><br />
                {analysis.investigation?.summary}
              </p>
              <p style={{ marginBottom: 8 }}>
                <span style={{ color: "#9ca3af", fontSize: 13 }}>Why it's suspicious</span><br />
                {analysis.investigation?.reason}
              </p>
            </Card>

            {/* Entities */}
            <Card>
              <SectionTitle emoji="📞" title="Extracted Entities" />
              {Object.entries(entities).some(([, v]) => Array.isArray(v) && (v as any[]).length > 0) ? (
                Object.entries(entities).map(([type, values]) => {
                  if (!Array.isArray(values) || values.length === 0) return null;
                  return (
                    <div key={type} style={{ marginBottom: 10 }}>
                      <span style={{ fontSize: 12, color: "#9ca3af", textTransform: "uppercase", letterSpacing: 1 }}>
                        {type.replace(/_/g, " ")}
                      </span>
                      <div style={{ marginTop: 4 }}>
                        {(values as string[]).map((v, i) => (
                          <EntityBadge key={i} value={v} color={ENTITY_COLORS[type] ?? "#4b5563"} />
                        ))}
                      </div>
                    </div>
                  );
                })
              ) : (
                <p style={{ color: "#6b7280" }}>No specific entities extracted.</p>
              )}
            </Card>

            {/* Intelligence */}
            <Card>
              <SectionTitle emoji="🕸️" title="Fraud Intelligence" />
              {analysis.intelligence?.campaign_detected ? (
                <div style={{ background: "#450a0a", border: "1px solid #dc2626", borderRadius: 8, padding: "10px 14px", marginBottom: 12, color: "#fca5a5" }}>
                  🚨 Campaign detected — this scam is linked to {analysis.intelligence.match_count} other complaint{analysis.intelligence.match_count > 1 ? "s" : ""}
                </div>
              ) : (
                <p style={{ color: "#9ca3af", marginBottom: 12 }}>
                  {analysis.intelligence?.match_count > 0
                    ? `Matched ${analysis.intelligence.match_count} related complaint — isolated activity`
                    : "No related complaints found — appears to be an isolated incident"}
                </p>
              )}
              {analysis.intelligence?.matched_complaints &&
                Object.keys(analysis.intelligence.matched_complaints).length > 0 && (
                <div>
                  <span style={{ fontSize: 12, color: "#9ca3af", textTransform: "uppercase", letterSpacing: 1 }}>
                    Linked Complaints
                  </span>
                  {Object.entries(analysis.intelligence.matched_complaints).map(([id, matches]: any) => (
                    <div key={id} style={{ marginTop: 6, background: "#1f2028", borderRadius: 6, padding: "8px 12px", fontSize: 13 }}>
                      <strong style={{ color: "#c084fc" }}>{id}</strong>
                      <span style={{ color: "#6b7280", marginLeft: 8 }}>
                        via {matches.map((m: any) => m.entity_type.replace(/_/g, " ")).join(", ")}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            {/* Victim Guidance */}
            {analysis.guidance && (
              <Card>
                <SectionTitle emoji="🆘" title="What To Do Now" />
                <div style={{
                  background: "#1e3a5f",
                  border: "1px solid #2563eb",
                  borderRadius: 8,
                  padding: "10px 16px",
                  marginBottom: 16,
                  fontSize: 14,
                  color: "#bfdbfe",
                  display: "flex",
                  gap: 16,
                  flexWrap: "wrap",
                }}>
                  <span>📞 Helpline: <strong>{analysis.guidance.helpline}</strong></span>
                  <span>🌐 Portal: <a href={analysis.guidance.portal} target="_blank" rel="noreferrer" style={{ color: "#60a5fa" }}>{analysis.guidance.portal}</a></span>
                </div>

                {analysis.guidance.steps?.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <p style={{ fontSize: 13, color: "#9ca3af", marginBottom: 8 }}>STEPS</p>
                    <ol style={{ margin: 0, paddingLeft: 20, lineHeight: 1.9, color: "#d1d5db" }}>
                      {analysis.guidance.steps.map((s: string, i: number) => <li key={i}>{s}</li>)}
                    </ol>
                  </div>
                )}

                {analysis.guidance.do_not?.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <p style={{ fontSize: 13, color: "#f87171", marginBottom: 8 }}>DO NOT</p>
                    <ul style={{ margin: 0, paddingLeft: 20, lineHeight: 1.9, color: "#d1d5db" }}>
                      {analysis.guidance.do_not.map((s: string, i: number) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>
                )}

                {analysis.guidance.preserve_evidence?.length > 0 && (
                  <div>
                    <p style={{ fontSize: 13, color: "#9ca3af", marginBottom: 8 }}>PRESERVE AS EVIDENCE</p>
                    <ul style={{ margin: 0, paddingLeft: 20, lineHeight: 1.9, color: "#d1d5db" }}>
                      {analysis.guidance.preserve_evidence.map((s: string, i: number) => <li key={i}>📎 {s}</li>)}
                    </ul>
                  </div>
                )}
              </Card>
            )}

            {/* Intelligence Report */}
            <Card>
              <SectionTitle emoji="📄" title="Intelligence Report" />
              {analysis.report?.executive_summary && (
                <div style={{ marginBottom: 16 }}>
                  <p style={{ fontSize: 13, color: "#9ca3af", marginBottom: 6 }}>EXECUTIVE SUMMARY</p>
                  <p style={{ lineHeight: 1.7 }}>{analysis.report.executive_summary}</p>
                </div>
              )}
              {analysis.report?.campaign_summary && (
                <div style={{ marginBottom: 16 }}>
                  <p style={{ fontSize: 13, color: "#9ca3af", marginBottom: 6 }}>CAMPAIGN SUMMARY</p>
                  <p style={{ lineHeight: 1.7 }}>{analysis.report.campaign_summary}</p>
                </div>
              )}
              {analysis.report?.recommended_actions?.length > 0 && (
                <div>
                  <p style={{ fontSize: 13, color: "#9ca3af", marginBottom: 8 }}>RECOMMENDED ACTIONS</p>
                  <ul style={{ margin: 0, paddingLeft: 20, lineHeight: 1.9 }}>
                    {analysis.report.recommended_actions.map((a: string, i: number) => (
                      <li key={i}>{a}</li>
                    ))}
                  </ul>
                </div>
              )}
              <div style={{ marginTop: 16, textAlign: "right" }}>
                <button
                  onClick={() => navigator.clipboard.writeText(JSON.stringify(analysis.report, null, 2))}
                  style={{
                    background: "transparent",
                    border: "1px solid #374151",
                    color: "#9ca3af",
                    borderRadius: 6,
                    padding: "6px 14px",
                    fontSize: 13,
                    cursor: "pointer",
                  }}
                >
                  📋 Copy Report
                </button>
              </div>
            </Card>

            {/* Crisis Companion */}
            <CrisisCompanion analysis={analysis} />
          </>
        )}
      </div>
    </div>
  );
}

export default App;
