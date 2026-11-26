"use client";

import { python } from "@codemirror/lang-python";
import { indentUnit } from "@codemirror/language";
import { keymap } from "@codemirror/view";
import dynamic from "next/dynamic";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  api,
  Exercise,
  ExerciseHelpState,
  Lesson,
  RunResult,
  streamExerciseCoach,
  streamReview,
  streamWalkthrough,
} from "@/lib/api";
import { useResolvedTheme } from "@/lib/prefs";
import { stripTopic, TRIAL_STARTER } from "@/lib/trial";
import FailureCards from "./FailureCards";
import Icon from "./Icon";
import Markdown from "./Markdown";
import VideoSegment from "./VideoSegment";

const CodeMirror = dynamic(() => import("@uiw/react-codemirror"), { ssr: false });

type Props = {
  lesson: Lesson;
  onSolved: (exerciseId: string) => void;
  onAskClaude: (text: string) => void;
  onActive?: (exercise: Exercise) => void; // tells the page which exercise is open (for doubts)
};

const VERDICT_KIND: Record<string, string> = { CORRECT: "good", PARTIAL: "warn", INCORRECT: "bad" };

// In the plan, only the first exercise of a GenAI / Agentic lesson is needed; the rest are bonus.
const SOFT_GATE_TRACKS = new Set(["genai", "agentic"]);
const WALKTHROUGH_MIN_FAILS = 3;
const MAX_HINT_LEVEL = 3;

export default function Practice({ lesson, onSolved, onAskClaude, onActive }: Props) {
  const theme = useResolvedTheme();
  const [exId, setExId] = useState(lesson.exercises[0].id);
  // Editor text per exercise: last submitted code, else the starter.
  const [codes, setCodes] = useState<Record<string, string>>(() =>
    Object.fromEntries(lesson.exercises.map((e) => [e.id, e.latest_code ?? e.starter])),
  );
  const [running, setRunning] = useState<"" | "tests" | "review">("");
  const [run, setRun] = useState<RunResult | null>(null);
  const [review, setReview] = useState("");
  const [error, setError] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);
  // Help used per exercise (Coach level, failed runs, walkthrough), starting from what the server knows.
  const [helps, setHelps] = useState<Record<string, ExerciseHelpState>>(() =>
    Object.fromEntries(lesson.exercises.map((e) => [e.id, e.help])),
  );
  const [helpText, setHelpText] = useState<{ kind: "coach" | "walkthrough"; text: string } | null>(null);
  const [helping, setHelping] = useState(false);

  const exIndex = lesson.exercises.findIndex((e) => e.id === exId);
  const ex = lesson.exercises[exIndex] as Exercise;
  const code = codes[exId];
  const setCode = (v: string) => setCodes((c) => ({ ...c, [exId]: v }));
  const help = helps[exId] ?? { coach_level: 0, walkthrough: false, fails: 0, walkthrough_ready: false };
  const setHelp = (patch: Partial<ExerciseHelpState>) =>
    setHelps((h) => {
      const next = { ...help, ...h[exId], ...patch };
      next.walkthrough_ready = next.fails >= WALKTHROUGH_MIN_FAILS && next.coach_level >= MAX_HINT_LEVEL;
      return { ...h, [exId]: next };
    });
  const softGate = SOFT_GATE_TRACKS.has(lesson.track);

  useEffect(() => {
    onActive?.(ex);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [exId]);

  const submit = async (file?: File) => {
    if (running) return;
    setError("");
    setRun(null);
    setReview("");
    setRunning("tests");
    try {
      if (file) setCode(await file.text()); // show exactly what was submitted
      const r = await api.runCode(lesson.id, exId, file ?? code);
      setRun(r);
      // Failing runs are usually mid-work, so Claude reviews them only when asked (saves usage).
      if (r.passed) {
        onSolved(exId);
        await requestReview(r.submission_id);
      } else {
        setHelp({ fails: help.fails + 1 });
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setRunning("");
    }
  };

  const askCoach = async () => {
    if (helping) return;
    const level = Math.min(help.coach_level + 1, MAX_HINT_LEVEL);
    setHelping(true);
    setError("");
    setHelpText({ kind: "coach", text: "" });
    try {
      await streamExerciseCoach(lesson.id, exId, code, run?.output ?? "", level, (t) =>
        setHelpText({ kind: "coach", text: stripTopic(t) }),
      );
      setHelp({ coach_level: Math.max(help.coach_level, level) });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setHelping(false);
    }
  };

  const askWalkthrough = async () => {
    if (helping) return;
    setHelping(true);
    setError("");
    setHelpText({ kind: "walkthrough", text: "" });
    try {
      await streamWalkthrough(lesson.id, exId, code, run?.output ?? "", (t) =>
        setHelpText({ kind: "walkthrough", text: stripTopic(t) }),
      );
      setHelp({ walkthrough: true });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setHelping(false);
    }
  };

  const requestReview = async (submissionId: number) => {
    setRunning("review");
    try {
      await streamReview(submissionId, setReview);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setRunning("");
    }
  };

  // Ctrl/Cmd+Enter runs the tests. The ref lets the keymap see the latest code.
  const submitRef = useRef(submit);
  submitRef.current = submit;
  const extensions = useMemo(
    () => [python(), indentUnit.of("    "), keymap.of([{ key: "Mod-Enter", run: () => (submitRef.current(), true) }])],
    [],
  );

  const verdict = review.match(/VERDICT:\s*(\w+)/)?.[1];
  const reviewBody = review.replace(/^\s*VERDICT:.*\n?/, "");

  const switchTo = (id: string) => {
    setExId(id);
    setRun(null);
    setReview("");
    setError("");
    setHelpText(null);
  };

  const next = lesson.exercises[exIndex + 1];

  return (
    <div className="practice">
      <div className="ex-tabs">
        {lesson.exercises.map((e, i) => (
          <button key={e.id} className={`ex-tab ${e.id === exId ? "active" : ""}`} onClick={() => switchTo(e.id)}>
            <span className={`ex-num ${e.solved ? "solved" : ""}`}>
              {e.solved ? <Icon name="check" size={11} /> : i + 1}
            </span>
            {e.title}
            {softGate && i > 0 && <span className="tag">bonus</span>}
          </button>
        ))}
      </div>

      <div className="card ex-prompt">
        <div className="card-label">
          Exercise {exIndex + 1} of {lesson.exercises.length}
          {softGate && (exIndex === 0 ? " · needed for the plan" : " · bonus (optional)")}
          {ex.solved && help.walkthrough && <span className="pill warn">solved with help</span>}
        </div>
        <h3>{ex.title}</h3>
        <Markdown text={ex.prompt} />
      </div>

      {ex.tools.length > 0 && (
        <details className="card tools-box">
          <summary>Tools you will need ({ex.tools.length})</summary>
          <ul>
            {ex.tools.map((t) => (
              <li key={t.name}>
                <Markdown text={t.name} inline />
                {t.lesson_id && (
                  <a href={`/${t.lesson_id}`} target="_blank" rel="noreferrer" className="muted">
                    lesson
                  </a>
                )}
              </li>
            ))}
          </ul>
        </details>
      )}

      {ex.video && <VideoSegment video={ex.video} label="Watch this problem being solved" />}

      <div className="editor-card">
        <div className="editor-bar">
          <span className="file-name">solution.py</span>
          <div className="editor-bar-actions">
            <button className="btn ghost small" onClick={() => fileInput.current?.click()} disabled={!!running}>
              <Icon name="upload" size={13} /> Upload .py
            </button>
            <button
              className="btn ghost small"
              onClick={() => confirm("Replace your code with the starter?") && setCode(ex.starter)}
            >
              <Icon name="reset" size={13} /> Reset
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
        <input
          ref={fileInput}
          type="file"
          accept=".py"
          hidden
          onChange={(e) => {
            const f = e.target.files?.[0];
            e.target.value = "";
            if (f) submit(f);
          }}
        />
      </div>

      <div className="run-bar">
        <button className="btn primary" onClick={() => submit()} disabled={!!running}>
          {running ? <span className="spinner" /> : <Icon name="play" size={13} />}
          {running === "tests" ? "Running tests…" : running === "review" ? "Claude is reviewing…" : "Run tests"}
          {!running && <kbd>⌘↵</kbd>}
        </button>
        <button className="btn" onClick={askCoach} disabled={helping}>
          {helping && helpText?.kind === "coach" ? <span className="spinner" /> : <Icon name="sparkle" size={13} />}
          Coach me (hint {Math.min(help.coach_level + 1, MAX_HINT_LEVEL)}/{MAX_HINT_LEVEL})
        </button>
        <button
          className="btn"
          onClick={askWalkthrough}
          disabled={helping || !help.walkthrough_ready}
          title={
            help.walkthrough_ready
              ? "A step-by-step walkthrough. You still write the code."
              : `Opens after ${WALKTHROUGH_MIN_FAILS} failed test runs (now ${help.fails}) and hint ${MAX_HINT_LEVEL} (now ${help.coach_level}).`
          }
        >
          <Icon name="sparkle" size={13} /> Walkthrough
        </button>
        <button
          className="btn"
          onClick={() =>
            onAskClaude(
              `I'm stuck on the exercise "${ex.title}". Here is my code:\n\n\`\`\`python\n${code}\n\`\`\`\n\nGive me a hint, not the full solution.`,
            )
          }
        >
          <Icon name="sparkle" size={13} /> Ask in chat
        </button>
        <button
          className="btn"
          title="Copy this code into the trial room: run it freely and get a comment-only plan"
          onClick={() => {
            const old = localStorage.getItem("trial.code");
            if (old && old !== TRIAL_STARTER && !confirm("Replace the code in the trial room?")) return;
            localStorage.setItem(
              "trial.code",
              `# PROBLEM: exercise "${ex.title}". Write what you are stuck on here.\n\n${code}\n`,
            );
            localStorage.setItem("trial.from", window.location.pathname + window.location.search);
            window.location.href = "/trial";
          }}
        >
          <Icon name="play" size={13} /> Try in trial room
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {helpText && (
        <div className="card help-card">
          <div className="card-label">
            {helpText.kind === "coach" ? `Coach · hint ${help.coach_level || 1}` : "Walkthrough"}
            <button className="btn ghost small push-right" onClick={() => setHelpText(null)}>
              <Icon name="x" size={12} />
            </button>
          </div>
          {helpText.text ? (
            helpText.kind === "coach" ? (
              <pre className="term">{helpText.text}</pre>
            ) : (
              <Markdown text={helpText.text} />
            )
          ) : (
            <div className="typing">
              <span />
              <span />
              <span />
            </div>
          )}
        </div>
      )}

      {run && (
        <div className="card result">
          <div className="result-head">
            <span className={`pill ${run.passed ? "good" : "bad"}`}>
              <Icon name={run.passed ? "check" : "x"} size={12} />
              {run.passed ? "Tests passed" : "Tests failed"}
            </span>
            <span className="muted">
              {run.summary} · {run.seconds.toFixed(1)}s
            </span>
            {run.passed && next && (
              <button className="btn small soft push-right" onClick={() => switchTo(next.id)}>
                Next exercise <Icon name="arrowRight" size={12} />
              </button>
            )}
          </div>
          {!run.passed && <FailureCards failures={run.failures} />}
          <details open={!run.passed && !run.failures?.length}>
            <summary>Full pytest output</summary>
            <pre className="term">{run.output || "(no output)"}</pre>
          </details>
          <div className="review">
            <div className="review-head">
              <span className="claude-mark tiny">
                <Icon name="sparkle" size={10} />
              </span>
              Claude review
              <span className={`pill ${verdict ? (VERDICT_KIND[verdict] ?? "neutral") : "neutral"}`}>
                {verdict ? verdict.toLowerCase() : running === "review" ? "reviewing…" : "—"}
              </span>
            </div>
            {reviewBody ? (
              <Markdown text={reviewBody} />
            ) : !running && !run.passed ? (
              <button className="btn small" onClick={() => requestReview(run.submission_id)}>
                <Icon name="sparkle" size={12} /> Ask Claude to review this attempt
              </button>
            ) : (
              running === "review" && (
                <div className="typing">
                  <span />
                  <span />
                  <span />
                </div>
              )
            )}
          </div>
        </div>
      )}
    </div>
  );
}
