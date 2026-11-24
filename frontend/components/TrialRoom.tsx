"use client";

import { python } from "@codemirror/lang-python";
import { indentUnit } from "@codemirror/language";
import { keymap } from "@codemirror/view";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  api,
  DrillCheck,
  ScriptResult,
  streamCoach,
  streamTrialChat,
  TrialDrill,
  TrialTurn,
  WeakTopic,
} from "@/lib/api";
import { useResolvedTheme } from "@/lib/prefs";
import {
  drillToEditor,
  findProblem,
  insertCoach,
  stripTopic,
  toComments,
  TRIAL_STARTER,
} from "@/lib/trial";
import Icon from "./Icon";
import Markdown from "./Markdown";

const CodeMirror = dynamic(() => import("@uiw/react-codemirror"), {
  ssr: false,
});

const DRAFT_KEY = "trial.code";
const CHAT_KEY = "trial.chat";
const FROM_KEY = "trial.from";

export default function TrialRoom() {
  const theme = useResolvedTheme();
  const [code, setCode] = useState(TRIAL_STARTER);
  const [loaded, setLoaded] = useState(false);
  const [exitHref, setExitHref] = useState("/");
  const [result, setResult] = useState<ScriptResult | null>(null);
  const [running, setRunning] = useState<"" | "run" | "coach" | "check">("");
  const [preview, setPreview] = useState("");
  const [before, setBefore] = useState<string | null>(null); // code before the last coach insert (for Undo)
  const [error, setError] = useState("");
  const [topics, setTopics] = useState<WeakTopic[]>([]);
  const attempts = useRef({ problem: "", n: 0 });
  const [chat, setChat] = useState<TrialTurn[]>([]);
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const chatEnd = useRef<HTMLDivElement>(null);

  // Drills
  const [drills, setDrills] = useState<Record<string, TrialDrill[]>>({});
  const [openTag, setOpenTag] = useState<string | null>(null);
  const [making, setMaking] = useState("");
  const [active, setActive] = useState<TrialDrill | null>(null);
  const [check, setCheck] = useState<DrillCheck | null>(null);
  const lastLoaded = useRef(""); // the editor text right after a drill was loaded

  const refreshTopics = () =>
    api
      .trialTopics()
      .then(setTopics)
      .catch(() => {});

  useEffect(() => {
    const saved = localStorage.getItem(DRAFT_KEY);
    if (saved) setCode(saved);
    try {
      setChat(JSON.parse(localStorage.getItem(CHAT_KEY) ?? "[]"));
    } catch {}
    setExitHref(localStorage.getItem(FROM_KEY) || "/");
    setLoaded(true);
    refreshTopics();
  }, []);

  useEffect(() => {
    if (loaded) localStorage.setItem(DRAFT_KEY, code);
  }, [code, loaded]);

  useEffect(() => {
    if (loaded && !asking)
      localStorage.setItem(CHAT_KEY, JSON.stringify(chat.slice(-20)));
  }, [chat, loaded, asking]);

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ block: "nearest" });
  }, [chat]);

  const lastOutput = () =>
    result ? [result.stdout, result.stderr].filter(Boolean).join("\n") : "";

  const ask = async () => {
    const message = question.trim();
    if (!message || asking) return;
    const history = chat;
    setQuestion("");
    setAsking(true);
    setChat([
      ...history,
      { role: "user", content: message },
      { role: "assistant", content: "" },
    ]);
    // The TOPIC line is for the app: never show it and never send it back.
    const show = (text: string) =>
      setChat([
        ...history,
        { role: "user", content: message },
        { role: "assistant", content: stripTopic(text) },
      ]);
    try {
      await streamTrialChat(message, code, lastOutput(), history, show);
    } catch (e) {
      show(`Could not reach Claude: ${(e as Error).message}`);
    } finally {
      setAsking(false);
      refreshTopics();
    }
  };

  const run = async () => {
    if (running) return;
    setError("");
    setRunning("run");
    try {
      setResult(await api.trialRun(code));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setRunning("");
    }
  };

  const coach = async () => {
    if (running) return;
    const problem = findProblem(code);
    if (!problem) {
      setError(
        "Add a comment that starts with  # PROBLEM:  and say what you are stuck on.",
      );
      return;
    }
    setError("");
    // Same problem text again = a deeper hint. A new problem text starts again at level 1.
    const a = attempts.current;
    a.n = a.problem === problem.text ? Math.min(a.n + 1, 3) : 1;
    a.problem = problem.text;
    const level = a.n;
    const output = lastOutput();
    setRunning("coach");
    setPreview("");
    try {
      const full = await streamCoach(code, output, level, (t) =>
        setPreview(toComments(t)),
      );
      const next = insertCoach(code, full, level);
      if (next) {
        setBefore(code);
        setCode(next);
      }
      setPreview("");
      refreshTopics();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setRunning("");
    }
  };

  // ---- drills ----

  const showDrills = async (tag: string) => {
    if (openTag === tag) return setOpenTag(null);
    setOpenTag(tag);
    try {
      setDrills((d) => ({ ...d, [tag]: [] }));
      const list = await api.trialDrills(tag);
      setDrills((d) => ({ ...d, [tag]: list }));
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const makeDrills = async (tag: string) => {
    if (making) return;
    setError("");
    setMaking(tag);
    try {
      const list = await api.makeDrills(tag);
      const done = (await api.trialDrills(tag)).filter(
        (d) => d.status === "done",
      );
      setDrills((d) => ({
        ...d,
        [tag]: [
          ...done,
          ...list.filter((x) => !done.some((y) => y.id === x.id)),
        ],
      }));
      setOpenTag(tag);
      refreshTopics();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setMaking("");
    }
  };

  const loadDrill = (d: TrialDrill) => {
    const untouched =
      code.trim() === "" ||
      code === TRIAL_STARTER ||
      code === lastLoaded.current;
    if (
      !untouched &&
      !confirm("Replace the code in the editor with this drill?")
    )
      return;
    const text = drillToEditor(d);
    lastLoaded.current = text;
    setCode(text);
    setBefore(null);
    setResult(null);
    setCheck(null);
    setActive(d);
    setError("");
  };

  const checkDrill = async () => {
    if (!active || running) return;
    setError("");
    setRunning("check");
    try {
      const r = await api.checkDrill(active.id, code);
      setCheck(r);
      if (r.passed) {
        const solved = { ...active, status: "done" as const };
        setActive(solved);
        setDrills((all) => ({
          ...all,
          [active.tag]: (all[active.tag] ?? []).map((x) =>
            x.id === active.id ? solved : x,
          ),
        }));
        refreshTopics();
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setRunning("");
    }
  };

  const nextOpenDrill = active
    ? (drills[active.tag] ?? []).find(
        (x) => x.status === "open" && x.id !== active.id,
      )
    : undefined;

  const runRef = useRef(run);
  runRef.current = run;
  const extensions = useMemo(
    () => [
      python(),
      indentUnit.of("    "),
      keymap.of([{ key: "Mod-Enter", run: () => (runRef.current(), true) }]),
    ],
    [],
  );

  return (
    <main className="trial">
      <div className="trial-left">
        <div className="trial-head">
          <Link
            href={exitHref}
            className="btn ghost small"
            title="Leave the trial room (your code is kept)"
          >
            <Icon name="arrowLeft" size={14} /> Exit
          </Link>
          <h1>Trial room</h1>
        </div>
        <p className="muted">
          Write code and run it. Stuck? Write a comment that starts with{" "}
          <code># PROBLEM:</code>, then press <b>Coach me</b>. Claude adds a
          plan as comments (never code). You write the code.
        </p>

        <div className="editor-card">
          <div className="editor-bar">
            <span className="file-name">
              {active ? `main.py · drill: ${active.title}` : "main.py"}
            </span>
            <div className="editor-bar-actions">
              {before !== null && (
                <button
                  className="btn ghost small"
                  onClick={() => {
                    setCode(before);
                    setBefore(null);
                  }}
                >
                  <Icon name="reset" size={13} /> Undo coach
                </button>
              )}
              <button
                className="btn ghost small"
                onClick={() =>
                  confirm("Clear the editor?") &&
                  (setCode(TRIAL_STARTER),
                  setBefore(null),
                  setResult(null),
                  setActive(null),
                  setCheck(null))
                }
              >
                <Icon name="reset" size={13} /> New
              </button>
            </div>
          </div>
          <CodeMirror
            value={code}
            onChange={setCode}
            extensions={extensions}
            theme={theme}
            minHeight="320px"
            basicSetup={{ tabSize: 4 }}
          />
        </div>

        <div className="run-bar">
          <button className="btn primary" onClick={run} disabled={!!running}>
            {running === "run" ? (
              <span className="spinner" />
            ) : (
              <Icon name="play" size={13} />
            )}
            {running === "run" ? "Running…" : "Run"}
            {!running && <kbd>⌘↵</kbd>}
          </button>
          <button className="btn" onClick={coach} disabled={!!running}>
            {running === "coach" ? (
              <span className="spinner" />
            ) : (
              <Icon name="sparkle" size={13} />
            )}
            {running === "coach" ? "Coach is writing…" : "Coach me"}
          </button>
          {active && (
            <button className="btn" onClick={checkDrill} disabled={!!running}>
              {running === "check" ? (
                <span className="spinner" />
              ) : (
                <Icon name="check" size={13} />
              )}
              {running === "check" ? "Checking…" : "Check drill"}
            </button>
          )}
        </div>

        {error && <p className="error">{error}</p>}

        {running === "coach" && preview && (
          <div className="card">
            <div className="card-label">
              Coach (will be added under your PROBLEM comment)
            </div>
            <pre className="term">{preview}</pre>
          </div>
        )}

        {check && active && (
          <div className="card result">
            <div className="result-head">
              <span className={`pill ${check.passed ? "good" : "bad"}`}>
                <Icon name={check.passed ? "check" : "x"} size={12} />
                {check.passed ? "Drill solved" : "Not yet"}
              </span>
              <span className="muted">{active.title}</span>
              {check.passed && nextOpenDrill && (
                <button
                  className="btn small soft push-right"
                  onClick={() => loadDrill(nextOpenDrill)}
                >
                  Next drill <Icon name="arrowRight" size={12} />
                </button>
              )}
            </div>
            {check.error && <pre className="term term-err">{check.error}</pre>}
            {check.results.length > 0 && (
              <ul className="check-list">
                {check.results.map((r) => (
                  <li key={r.call} className={r.ok ? "ok" : "bad"}>
                    <Icon name={r.ok ? "check" : "x"} size={12} />
                    <code>{r.call}</code>
                    <span className="muted">
                      {r.ok
                        ? `→ ${r.got}`
                        : `gave ${r.got}, expected ${r.want}`}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {result && (
          <div className="card result">
            <div className="result-head">
              <span
                className={`pill ${result.timed_out || result.stderr ? "bad" : "good"}`}
              >
                <Icon
                  name={result.timed_out || result.stderr ? "x" : "check"}
                  size={12}
                />
                {result.timed_out
                  ? "Timed out"
                  : result.stderr
                    ? "Error"
                    : "Ran fine"}
              </span>
              <span className="muted">{result.seconds.toFixed(1)}s</span>
            </div>
            {result.stdout && <pre className="term">{result.stdout}</pre>}
            {result.stderr && (
              <pre className="term term-err">{result.stderr}</pre>
            )}
            {!result.stdout && !result.stderr && (
              <pre className="term">(no output: use print() to see values)</pre>
            )}
          </div>
        )}

        <section className="card">
          <div className="card-label">Your weak topics</div>
          {topics.length === 0 ? (
            <p className="muted">
              None yet. When you press Coach me, ask a question, or fail an
              exercise, the topic shows up here. Claude uses this list to help
              you better.
            </p>
          ) : (
            <ul className="weak-list">
              {topics.map((t) => (
                <li key={t.tag} className="weak-item">
                  <div className="weak-row">
                    <div className="weak-main">
                      <b>{t.title}</b>
                      <span className="muted">
                        {[
                          t.coach ? `stuck ${t.coach}×` : "",
                          t.chat ? `asked ${t.chat}×` : "",
                          ...t.failed.map(
                            (f) => `failed “${f.exercise}” ${f.fails}×`,
                          ),
                        ]
                          .filter(Boolean)
                          .join(" · ")}
                      </span>
                      {t.details.length > 0 && (
                        <span className="muted">{t.details.join("; ")}</span>
                      )}
                    </div>
                    <span
                      className={`pill ${t.score === 0 ? "good" : t.score >= 4 ? "bad" : "warn"}`}
                      title="Weak score: goes up when you get stuck, down when you solve drills"
                    >
                      {t.score === 0 ? "improving" : `score ${t.score}`}
                    </span>
                  </div>
                  <div className="weak-actions">
                    {t.tag !== "other" && (
                      <button
                        className="btn small"
                        onClick={() => makeDrills(t.tag)}
                        disabled={!!making}
                      >
                        {making === t.tag ? (
                          <span className="spinner" />
                        ) : (
                          <Icon name="sparkle" size={12} />
                        )}
                        {making === t.tag
                          ? "Claude is writing drills…"
                          : t.drills_total
                            ? "New drills"
                            : "Make drills"}
                      </button>
                    )}
                    {t.drills_total > 0 && (
                      <button
                        className="btn ghost small"
                        onClick={() => showDrills(t.tag)}
                      >
                        Drills {t.drills_done}/{t.drills_total}{" "}
                        {openTag === t.tag ? "▴" : "▾"}
                      </button>
                    )}
                  </div>
                  {openTag === t.tag && (
                    <ul className="drill-list">
                      {(drills[t.tag] ?? []).map((d, i) => (
                        <li key={d.id}>
                          <button
                            className={`drill ${active?.id === d.id ? "active" : ""}`}
                            onClick={() => loadDrill(d)}
                          >
                            <span
                              className={`ex-num ${d.status === "done" ? "solved" : ""}`}
                            >
                              {d.status === "done" ? (
                                <Icon name="check" size={11} />
                              ) : (
                                i + 1
                              )}
                            </span>
                            {d.title}
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      <aside className="card trial-chat trial-right">
        <div
          className="card-label"
          style={{ display: "flex", justifyContent: "space-between" }}
        >
          <span>Ask Claude (it sees your code and the last output)</span>
          {chat.length > 0 && (
            <button
              className="btn ghost small"
              disabled={asking}
              onClick={() => setChat([])}
            >
              Clear
            </button>
          )}
        </div>
        {chat.length === 0 && (
          <p className="muted">
            Ask anything: &quot;what does .items() do?&quot;, &quot;why this
            error?&quot;. Claude explains, it does not write your solution. It
            also knows your weak topics, so it can explain those more simply.
          </p>
        )}
        <div className="trial-chat-log">
          {chat.map((m, i) => (
            <div key={i} className={`msg ${m.role}`}>
              {m.role === "assistant" ? (
                m.content ? (
                  <Markdown text={stripTopic(m.content)} />
                ) : (
                  <div className="typing">
                    <span />
                    <span />
                    <span />
                  </div>
                )
              ) : (
                m.content
              )}
            </div>
          ))}
          <div ref={chatEnd} />
        </div>
        <div className="trial-chat-input">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (
                e.key === "Enter" &&
                !e.shiftKey &&
                !e.nativeEvent.isComposing
              ) {
                e.preventDefault();
                ask();
              }
            }}
            placeholder="Ask a question…  (Enter to send, Shift+Enter for a new line)"
            rows={2}
          />
          <button
            className="btn primary"
            onClick={ask}
            disabled={asking || !question.trim()}
          >
            {asking ? (
              <span className="spinner" />
            ) : (
              <Icon name="sparkle" size={13} />
            )}{" "}
            Ask
          </button>
        </div>
      </aside>
    </main>
  );
}
