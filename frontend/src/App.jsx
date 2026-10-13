import { useCallback, useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";
const TOKEN_KEY = "resumeAnalyzerToken";

const CSS = `
* { box-sizing: border-box; }
body { margin: 0; background: #080d1b; color: #f1f5f9; font-family: Arial, Helvetica, sans-serif; }
button, input, textarea { font: inherit; }
button { cursor: pointer; }
button:disabled { opacity: .6; cursor: not-allowed; }
.app { min-height: 100vh; }
.header { background: #0c1325; border-bottom: 1px solid #26344e; padding: 22px 24px; }
.header-inner, .container { max-width: 1160px; width: 100%; margin: 0 auto; }
.brand { margin: 0 0 7px; font-size: 25px; font-weight: 800; }
.subtitle { margin: 0; color: #a3b2cb; line-height: 1.55; }
.container { padding: 27px 20px 58px; }
.panel { min-width: 0; margin-bottom: 21px; padding: 22px; border: 1px solid #293750; border-radius: 16px; background: #10192c; }
.panel h2 { margin: 0 0 9px; font-size: 21px; }
.panel h3 { margin: 0 0 13px; font-size: 16px; }
.muted { color: #a3b2cb; line-height: 1.6; }
.small { font-size: 13px; }
.field { display: flex; flex-direction: column; gap: 8px; margin: 17px 0; }
label { color: #dce5f4; font-size: 14px; font-weight: 650; }
input, textarea { width: 100%; padding: 12px 14px; background: #080f20; border: 1px solid #384761; border-radius: 10px; color: #f1f5f9; outline: none; }
input:focus, textarea:focus { border-color: #818cf8; }
textarea { min-height: 150px; resize: vertical; line-height: 1.6; }
input[type=file] { padding: 10px; }
.btn { padding: 12px 17px; border: 0; border-radius: 10px; background: linear-gradient(100deg, #2563eb, #7c3aed); color: #fff; font-weight: 700; }
.btn-secondary { background: #1b2940; border: 1px solid #3b4c67; }
.error, .success { padding: 13px 15px; border-radius: 10px; margin: 16px 0; overflow-wrap: anywhere; white-space: pre-wrap; }
.error { color: #fecaca; background: #29101b; border: 1px solid #8b263d; }
.success { color: #bbf7d0; background: #10271f; border: 1px solid #226849; }
.userbar { display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap; }
.auth-wrap { max-width: 480px; margin: 30px auto; }
.grid { display: grid; grid-template-columns: minmax(0, 1.3fr) minmax(260px, .8fr); gap: 21px; }
.section-heading { padding-bottom: 14px; margin-bottom: 16px; border-bottom: 1px solid #293750; }
.section-heading h2 { display: flex; align-items: center; gap: 9px; }
.section-number { display: inline-flex; width: 30px; height: 30px; align-items: center; justify-content: center; flex: 0 0 auto; border-radius: 9px; background: #24345a; color: #c7d2fe; font-size: 13px; }
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(175px, 1fr)); gap: 14px; margin-top: 17px; }
.metric-card { min-width: 0; padding: 17px; background: #0a1223; border: 1px solid #354461; border-radius: 13px; }
.metric-label { color: #a3b2cb; font-size: 13px; line-height: 1.5; }
.metric-value { margin: 12px 0; color: #c4b5fd; font-size: 30px; font-weight: 800; overflow-wrap: anywhere; }
.progress-track { height: 8px; background: #253149; border-radius: 20px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #3b82f6, #a855f7); border-radius: 20px; transition: width .35s ease; }
.count-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-top: 17px; }
.count-card { min-width: 0; padding: 15px; border: 1px solid #2b3b55; background: #111c31; border-radius: 12px; }
.count-value { margin-top: 8px; font-size: 24px; font-weight: 750; }
.result-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 15px; margin-top: 17px; }
.result-card { min-width: 0; padding: 17px; border: 1px solid #2b3b55; background: #0b1324; border-radius: 12px; overflow-wrap: anywhere; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { display: inline-block; max-width: 100%; padding: 7px 10px; border: 1px solid #3b4d6c; border-radius: 8px; background: #1a2943; color: #dbeafe; font-size: 13px; overflow-wrap: anywhere; }
.detail-row { display: flex; justify-content: space-between; gap: 14px; padding: 10px 0; border-bottom: 1px solid #293750; overflow-wrap: anywhere; }
.detail-row:last-child { border-bottom: none; }
.detail-label { color: #a3b2cb; }
.detail-value { max-width: 60%; text-align: right; font-weight: 650; overflow-wrap: anywhere; }
.history-item { display: block; width: 100%; margin-top: 10px; padding: 13px; text-align: left; color: #e2e8f0; background: #0b1324; border: 1px solid #33415b; border-radius: 10px; overflow-wrap: anywhere; }
.history-item:hover { border-color: #818cf8; }
.empty { color: #9caec8; line-height: 1.6; }
.download-panel { text-align: center; padding: 28px 20px; border-color: #45528d; background: #10182d; }
.report-btn { margin-top: 12px; padding: 15px 24px; }
.raw-response { margin-top: 22px; padding: 15px; background: #080f20; border: 1px solid #293751; border-radius: 10px; }
.raw-response summary { cursor: pointer; color: #a5b4fc; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; color: #dbeafe; font-size: 13px; line-height: 1.6; }
.footer { text-align: center; margin-top: 22px; color: #8191ac; font-size: 12px; }
@media (max-width: 760px) { .grid { grid-template-columns: 1fr; } .panel { padding: 17px; } .brand { font-size: 22px; } }
`;

function normalizedKey(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9]/g, "");
}

function findValueDeep(data, aliases, depth = 0) {
  if (data == null || typeof data !== "object" || depth > 10) return undefined;
  const wanted = new Set(aliases.map(normalizedKey));

  for (const [key, value] of Object.entries(data)) {
    if (wanted.has(normalizedKey(key)) && value !== null && value !== undefined) {
      return value;
    }
  }

  for (const value of Object.values(data)) {
    const found = findValueDeep(value, aliases, depth + 1);
    if (found !== undefined && found !== null) return found;
  }
  return undefined;
}

function toPercent(value) {
  if (value && typeof value === "object") {
    value = value.percentage ?? value.score ?? value.value ?? value.match_score;
  }
  if (value === null || value === undefined || value === "") return null;
  const original = String(value).trim();
  const n = Number(original.replace(/%$/, "").trim());
  if (!Number.isFinite(n)) return null;
  const percent = !original.includes("%") && n > 0 && n < 1 ? n * 100 : n;
  return Math.round(Math.min(100, Math.max(0, percent)));
}

function getCount(value) {
  if (value === null || value === undefined || value === "") return null;
  if (Array.isArray(value)) return value.length;
  if (typeof value === "object") {
    const count = value.count ?? value.total ?? value.length ?? value.value;
    return count == null ? null : getCount(count);
  }
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function displayValue(value) {
  if (value === undefined || value === null || value === "") return "Not returned by backend";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (Array.isArray(value)) return value.length ? value.map(displayValue).join(", ") : "None detected";
  if (typeof value === "object") {
    const candidate = value.name ?? value.text ?? value.label ?? value.status ?? value.value ?? value.score;
    return candidate === undefined ? JSON.stringify(value) : displayValue(candidate);
  }
  return String(value);
}

function toDisplayList(value) {
  if (value === undefined || value === null || value === "") return [];
  if (Array.isArray(value)) {
    return value.map((item) => {
      if (typeof item === "string" || typeof item === "number") return String(item);
      if (item && typeof item === "object") {
        return displayValue(item.name ?? item.skill ?? item.keyword ?? item.text ?? item.suggestion ?? item);
      }
      return String(item);
    }).filter(Boolean);
  }
  if (typeof value === "string") return value.split(/[\n,;]+/).map((item) => item.trim()).filter(Boolean);
  if (typeof value === "object") return Object.entries(value).map(([key, item]) => `${key}: ${displayValue(item)}`);
  return [String(value)];
}

async function parseResponse(response) {
  const text = await response.text();
  try {
    return { data: text ? JSON.parse(text) : {}, ok: response.ok, status: response.status };
  } catch {
    return { data: { message: text || "The server returned an unreadable response." }, ok: response.ok, status: response.status };
  }
}

function ScoreCard({ title, aliases, data }) {
  const score = toPercent(findValueDeep(data, aliases));
  return (
    <div className="metric-card">
      <div className="metric-label">{title}</div>
      <div className="metric-value">{score === null ? "N/A" : `${score}%`}</div>
      <div className="progress-track" aria-label={`${title} ${score ?? "unavailable"}`}>
        <div className="progress-fill" style={{ width: `${score ?? 0}%` }} />
      </div>
      {score === null && <p className="muted small">This field was not returned by the backend.</p>}
    </div>
  );
}

function CountCard({ title, aliases, data }) {
  const count = getCount(findValueDeep(data, aliases));
  return (
    <div className="count-card">
      <div className="metric-label">{title}</div>
      <div className="count-value">{count === null ? "N/A" : count}</div>
    </div>
  );
}

function ListCard({ title, aliases, data }) {
  const list = toDisplayList(findValueDeep(data, aliases));
  return (
    <section className="result-card">
      <h3>{title}</h3>
      {list.length === 0 ? (
        <p className="muted small">No data returned for this section.</p>
      ) : (
        <div className="chips">
          {list.map((item, index) => <span className="chip" key={`${title}-${index}`}>{item}</span>)}
        </div>
      )}
    </section>
  );
}

function DetailCard({ title, fields, data }) {
  return (
    <section className="result-card">
      <h3>{title}</h3>
      {fields.map((field) => (
        <div className="detail-row" key={field.label}>
          <span className="detail-label">{field.label}</span>
          <span className="detail-value">{displayValue(findValueDeep(data, field.aliases))}</span>
        </div>
      ))}
    </section>
  );
}

function SectionTitle({ number, title, description }) {
  return (
    <div className="section-heading">
      <h2><span className="section-number">{number}</span>{title}</h2>
      {description && <p className="muted small">{description}</p>}
    </div>
  );
}

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || "");
  const [user, setUser] = useState(null);
  const [checkingSession, setCheckingSession] = useState(true);
  const [registerMode, setRegisterMode] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [history, setHistory] = useState([]);
  const [busy, setBusy] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const showError = useCallback((message) => setError(message || "Something went wrong."), []);

  const loadHistory = useCallback(async (accessToken) => {
    const response = await fetch(`${API_URL}/history`, {
      method: "GET",
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    const result = await parseResponse(response);
    if (result.status === 401) throw new Error("Your login has expired. Please log in again.");
    if (!result.ok || result.data.success === false) {
      throw new Error(result.data.error || result.data.message || "Unable to load analysis history.");
    }
    const items = Array.isArray(result.data.history) ? result.data.history : [];
    setHistory(items);
  }, []);

  const clearSession = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken("");
    setUser(null);
    setAnalysis(null);
    setHistory([]);
    setError("");
    setNotice("You have logged out.");
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function checkExistingSession() {
      const savedToken = localStorage.getItem(TOKEN_KEY);
      if (!savedToken) {
        setCheckingSession(false);
        return;
      }

      try {
        const response = await fetch(`${API_URL}/me`, {
          method: "GET",
          headers: { Authorization: `Bearer ${savedToken}` },
        });
        const result = await parseResponse(response);
        if (!result.ok || result.data.success === false) {
          localStorage.removeItem(TOKEN_KEY);
          if (!cancelled) setToken("");
          return;
        }
        if (!cancelled) {
          setToken(savedToken);
          setUser(result.data.user || null);
        }
        await loadHistory(savedToken);
      } catch (err) {
        if (!cancelled) showError(`${err.message || "Failed to fetch"}. Check that Flask is running at ${API_URL}.`);
      } finally {
        if (!cancelled) setCheckingSession(false);
      }
    }

    checkExistingSession();
    return () => { cancelled = true; };
  }, [loadHistory, showError]);

  async function handleAuth(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");

    try {
      const endpoint = registerMode ? "/register" : "/login";
      const body = registerMode
        ? { name: name.trim(), email: email.trim(), password }
        : { email: email.trim(), password };

      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const result = await parseResponse(response);

      if (!result.ok || result.data.success === false) {
        throw new Error(result.data.error || result.data.message || "Authentication failed.");
      }

      if (registerMode) {
        setRegisterMode(false);
        setPassword("");
        setNotice("Account created. Please log in using your email and password.");
        return;
      }

      if (!result.data.token) throw new Error("The login response did not include an authentication token.");
      localStorage.setItem(TOKEN_KEY, result.data.token);
      setToken(result.data.token);
      setUser(result.data.user || { name, email: email.trim() });
      setPassword("");
      setNotice("Login successful.");
      await loadHistory(result.data.token);
    } catch (err) {
      showError(`${err.message || "Failed to fetch"}. Make sure the backend is running at ${API_URL}.`);
    } finally {
      setBusy(false);
    }
  }

  async function handleAnalyze(event) {
    event.preventDefault();
    setError("");
    setNotice("");
    setAnalysis(null);

    if (!token) return showError("Please log in before analyzing a resume.");
    if (!resume) return showError("Please select a resume file.");
    if (!jobDescription.trim()) return showError("Please enter the job description.");

    setBusy(true);
    try {
      const formData = new FormData();
      formData.append("resume", resume);
      formData.append("job_description", jobDescription.trim());

      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const result = await parseResponse(response);

      if (result.status === 401) {
        clearSession();
        throw new Error("Authentication expired. Please log in again.");
      }
      if (!result.ok || result.data.success === false) {
        throw new Error(result.data.error || result.data.message || "Resume analysis failed.");
      }

      setAnalysis(result.data);
      setNotice("Resume analysis completed. The dashboard and PDF use this response.");
      await loadHistory(token);
    } catch (err) {
      showError(err.message || "Resume analysis failed.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDownloadReport() {
    if (!analysis || !token) return showError("Analyze a resume before downloading a report.");
    setDownloading(true);
    setError("");
    setNotice("");

    try {
      const response = await fetch(`${API_URL}/download-report`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ analysis }),
      });

      if (!response.ok) {
        const result = await parseResponse(response);
        if (result.status === 401) clearSession();
        throw new Error(result.data.error || result.data.message || "PDF report generation failed.");
      }

      const contentType = response.headers.get("content-type") || "";
      if (!contentType.includes("application/pdf") && !contentType.includes("application/octet-stream")) {
        const result = await parseResponse(response);
        throw new Error(result.data.error || result.data.message || "The server did not return a PDF file.");
      }

      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = "resume-analysis-report.pdf";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(objectUrl);
      setNotice("Your analysis report has been downloaded.");
    } catch (err) {
      showError(err.message || "PDF report download failed.");
    } finally {
      setDownloading(false);
    }
  }

  function openHistoryItem(item) {
    const saved = item.analysis || item.analysis_json || item;
    if (typeof saved === "string") {
      try { setAnalysis(JSON.parse(saved)); }
      catch { showError("The saved analysis could not be read."); return; }
    } else {
      setAnalysis(saved);
    }
    setError("");
    setNotice("Loaded the selected saved analysis.");
  }

  const scoreMetrics = [
    { title: "Resume Match Score", aliases: ["resume_score", "overall_match_score", "overall_match_percentage", "resume_match_score", "match_score"] },
    { title: "Job Similarity", aliases: ["similarity_score", "job_similarity", "job_similarity_score", "job_similarity_percentage"] },
    { title: "Skill Match", aliases: ["skill_match", "skill_match_score", "skill_match_percentage"] },
    { title: "Role Keyword Match", aliases: ["role_keyword_match", "role_keyword_match_score", "role_keyword_match_percentage"] },
    { title: "ATS Score", aliases: ["ats_score", "ats_percentage", "ats_match_score"] },
  ];

  const currentName = user?.name || user?.email || email || "User";

  return (
    <div className="app">
      <style>{CSS}</style>
      <header className="header">
        <div className="header-inner">
          <h1 className="brand">🤖 AI Resume Analyzer</h1>
          <p className="subtitle">AI-powered resume analysis, ATS matching and suggestions</p>
        </div>
      </header>

      <main className="container">
        {checkingSession ? (
          <section className="panel"><p className="muted">Checking your login session...</p></section>
        ) : (!token || !user) ? (
          <div className="auth-wrap">
            <section className="panel">
              <h2>{registerMode ? "Create your account" : "Welcome back"}</h2>
              <p className="muted">{registerMode ? "Register to analyze resumes and save your results." : "Log in to analyze resumes and view saved results."}</p>
              {error && <div className="error">❌ {error}</div>}
              {notice && <div className="success">✓ {notice}</div>}
              <form onSubmit={handleAuth}>
                {registerMode && <div className="field"><label htmlFor="name">Full name</label><input id="name" value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" required placeholder="Enter your name" /></div>}
                <div className="field"><label htmlFor="email">Email address</label><input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" required placeholder="you@example.com" /></div>
                <div className="field"><label htmlFor="password">Password</label><input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete={registerMode ? "new-password" : "current-password"} minLength={registerMode ? 6 : undefined} required placeholder="Enter your password" /></div>
                <button className="btn" disabled={busy} type="submit">{busy ? "Please wait..." : registerMode ? "Create account" : "Log in"}</button>
              </form>
              <div style={{ marginTop: 20 }}>
                <p className="muted small">{registerMode ? "Already registered?" : "Don't have an account?"}</p>
                <button className="btn btn-secondary" type="button" onClick={() => { setRegisterMode((v) => !v); setError(""); setNotice(""); }}>{registerMode ? "Go to login" : "Create an account"}</button>
              </div>
              <p className="footer">Backend API: {API_URL}</p>
            </section>
          </div>
        ) : (
          <>
            <section className="panel">
              <div className="userbar">
                <div><h2>Welcome, {currentName}</h2><p className="muted small">Analyze a resume against a job description, view your scores, and download a report.</p></div>
                <button className="btn btn-secondary" onClick={clearSession} type="button">Log out</button>
              </div>
            </section>

            {error && <div className="error">❌ {error}</div>}
            {notice && <div className="success">✓ {notice}</div>}

            <section className="panel">
              <h2>Analyze Your Resume</h2>
              <p className="muted">Upload a text-based PDF, DOCX, or TXT resume. Then paste the target job description.</p>
              <form onSubmit={handleAnalyze}>
                <div className="field"><label htmlFor="resume">Resume file</label><input id="resume" type="file" accept=".pdf,.docx,.txt" onChange={(e) => { setResume(e.target.files?.[0] || null); setError(""); }} required />{resume && <span className="muted small">Selected: {resume.name}</span>}</div>
                <div className="field"><label htmlFor="jobDescription">Job description</label><textarea id="jobDescription" value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} required placeholder="Example: Python Developer, Python, Flask, REST APIs, SQL, Git, debugging..." /></div>
                <button className="btn" disabled={busy} type="submit">{busy ? "Analyzing resume..." : "Analyze Resume"}</button>
              </form>
            </section>

            {analysis && (
              <>
                <section className="panel"><SectionTitle number="01" title="Resume Match Score" description="Overall score calculated from similarity, skill coverage, ATS coverage, and role-specific keyword coverage." /><div className="metric-grid"><ScoreCard title="Resume Match Score" aliases={scoreMetrics[0].aliases} data={analysis} /></div></section>

                <section className="panel"><SectionTitle number="02" title="Detected Job Role" description="Role inferred from keywords in the job description." /><div className="result-card"><h3>Recommended or detected role</h3><p>{displayValue(findValueDeep(analysis, ["detected_job_role", "predicted_job_role", "job_role", "predicted_role", "role_name", "role"]))}</p></div></section>

                <section className="panel"><SectionTitle number="03" title="Job Similarity" description="Lexical text similarity between the resume and the job description; this is not semantic model output." /><div className="metric-grid"><ScoreCard title="Job Similarity" aliases={scoreMetrics[1].aliases} data={analysis} /></div></section>

                <section className="panel"><SectionTitle number="04" title="Skill Match" description="Percentage of detected job skills that also appear in the resume." /><div className="metric-grid"><ScoreCard title="Skill Match" aliases={scoreMetrics[2].aliases} data={analysis} /></div></section>

                <section className="panel"><SectionTitle number="05" title="ATS Score" description="Weighted job-keyword and resume-section coverage score." /><div className="metric-grid"><ScoreCard title="ATS Score" aliases={scoreMetrics[4].aliases} data={analysis} /></div><div className="count-grid"><CountCard title="Total Keywords" aliases={["total_keywords"]} data={analysis} /><CountCard title="Matched Keywords" aliases={["matched_keywords_count"]} data={analysis} /><CountCard title="Missing Keywords" aliases={["missing_keywords_count"]} data={analysis} /><CountCard title="Resume Word Count" aliases={["word_count", "resume_word_count"]} data={analysis} /></div></section>

                <section className="panel"><SectionTitle number="06" title="Resume Skills" description="Recognized skill terms detected in the extracted resume text." /><ListCard title="Detected Resume Skills" aliases={["resume_skills", "detected_skills", "extracted_skills", "skills"]} data={analysis} /><div style={{ marginTop: 14 }}><ListCard title="Required Job Skills" aliases={["required_skills", "job_skills", "required_job_skills"]} data={analysis} /></div></section>

                <section className="panel"><SectionTitle number="07" title="Matched Skills" description="Skills present in both the resume and job description." /><ListCard title="Matched Skills" aliases={["matched_skills", "skills_matched", "common_skills"]} data={analysis} /></section>

                <section className="panel"><SectionTitle number="08" title="Missing Skills" description="Job skills not found in the extracted resume text. Only add these if you genuinely have them." /><ListCard title="Potential Skill Gaps" aliases={["missing_skills", "skills_missing", "unmatched_skills"]} data={analysis} /></section>

                <section className="panel"><SectionTitle number="09" title="ATS Analysis" description="Keywords identified in the job description and matched against resume text." /><div className="result-grid"><ListCard title="Matched ATS Keywords" aliases={["matched_ats_keywords", "matched_keywords"]} data={analysis} /><ListCard title="Missing ATS Keywords" aliases={["missing_ats_keywords", "missing_keywords"]} data={analysis} /><ListCard title="Detected Role Keywords" aliases={["detected_role_keywords", "role_keywords"]} data={analysis} /></div></section>

                <section className="panel"><SectionTitle number="10" title="Resume Improvement Suggestions" description="Recommendations created from detected gaps in this analysis." /><ListCard title="Suggestions" aliases={["improvement_suggestions", "suggestions", "recommendations"]} data={analysis} /></section>

                <section className="panel"><SectionTitle number="11" title="Resume Section Check" description="Checks for common resume headings." /><div className="result-grid"><ListCard title="Found Sections" aliases={["found_sections", "sections_found"]} data={analysis} /><ListCard title="Missing Sections" aliases={["missing_sections", "sections_missing"]} data={analysis} /></div></section>

                <section className="panel"><SectionTitle number="12" title="Contact Information" description="Contact details detected by simple text patterns." /><DetailCard title="Contact details" data={analysis} fields={[{ label: "Email", aliases: ["resume_email", "email_address", "detected_email"] }, { label: "Phone", aliases: ["phone_number", "detected_phone", "resume_phone"] }]} /></section>

                <section className="panel"><SectionTitle number="13" title="Project Quality Check" description="Detected technologies, action verbs, and measurable outcomes in the resume text." /><DetailCard title="Project quality checks" data={analysis} fields={[{ label: "Technology Words", aliases: ["technology_words"] }, { label: "Action Words", aliases: ["action_words"] }, { label: "Numbers / Results", aliases: ["numbers_results"] }]} /></section>

                <section className="panel"><SectionTitle number="14" title="Scoring Method" description="The current implementation uses transparent keyword-based heuristics. It is not a trained AI model." /><DetailCard title="Score weights" data={analysis} fields={[{ label: "Method", aliases: ["type"] }, { label: "Weight details", aliases: ["resume_match_weights"] }]} /></section>
              </>
            )}

            <section className="panel">
              <SectionTitle number="15" title="Analysis History" description="Previously saved analysis results for this account." />
              <button className="btn btn-secondary" type="button" disabled={busy} onClick={async () => { setError(""); try { await loadHistory(token); setNotice("History refreshed."); } catch (err) { showError(err.message); } }}>Refresh History</button>
              {history.length === 0 ? <p className="empty">No saved analyses yet. Run an analysis and it will appear here.</p> : history.map((item, index) => (
                <button className="history-item" type="button" key={item.id || item.analysis_id || index} onClick={() => openHistoryItem(item)}>
                  <strong>{item.filename || `Analysis ${index + 1}`}</strong>
                  <div className="muted small" style={{ marginTop: 6 }}>{item.created_at || ""}</div>
                  <div className="muted small" style={{ marginTop: 5 }}>Resume match: {item.resume_score == null ? "N/A" : `${item.resume_score}%`} · ATS: {item.ats_score == null ? "N/A" : `${item.ats_score}%`}</div>
                </button>
              ))}
            </section>

            <section className="panel download-panel">
              <h2>📥 Download Analysis Report</h2>
              <p className="muted">Download a PDF report based on the same JSON response used by this dashboard.</p>
              <button className="btn report-btn" type="button" disabled={!analysis || downloading} onClick={handleDownloadReport}>{downloading ? "Generating report..." : "📥 Download Analysis Report"}</button>
              {!analysis && <p className="muted small">Analyze a resume first to enable PDF download.</p>}
            </section>

            {analysis && <details className="raw-response"><summary>View raw analysis JSON</summary><pre>{JSON.stringify(analysis, null, 2)}</pre></details>}
          </>
        )}
      </main>
    </div>
  );
}
