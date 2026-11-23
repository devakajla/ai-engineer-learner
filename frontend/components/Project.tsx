"use client";

import { useState } from "react";
import { api, CheckResult, Lesson, streamProjectReview } from "@/lib/api";
import FailureCards from "./FailureCards";
import Icon from "./Icon";
import Markdown from "./Markdown";

type Props = {
  lesson: Lesson;
  onPassed: () => void;
  onAskClaude: (text: string) => void;
};

const VERDICT_KIND: Record<string, string> = { CORRECT: "good", PARTIAL: "warn", INCORRECT: "bad" };

/** The lesson's project step: instructions + checkpoint tests on the learner's own folder + Claude review. */
export default function Project({ lesson, onPassed, onAskClaude }: Props) {
  const step = lesson.project!;
  const [dir, setDir] = useState(step.project_dir);
  const [savedDir, setSavedDir] = useState(step.project_dir);
  const [running, setRunning] = useState<"" | "tests" | "review">("");
  const [check, setCheck] = useState<CheckResult | null>(null);
  const [review, setReview] = useState("");
  const [error, setError] = useState("");

  const saveDir = async () => {
    const { project_dir } = await api.setProjectDir(lesson.track, dir);
    setDir(project_dir);
    setSavedDir(project_dir);
  };

  const runCheck = async () => {
    if (running) return;
    setError("");
    setCheck(null);
    setReview("");
    setRunning("tests");
    try {
      if (dir !== savedDir) await saveDir();
      const r = await api.checkProject(lesson.id);
      setCheck(r);
      // A failed checkpoint shows the test output; Claude reviews it only when asked (saves usage).
      if (r.passed) {
        onPassed();
        await requestReview(r.check_id);
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setRunning("");
    }
  };

  const requestReview = async (checkId: number) => {
    setRunning("review");
    try {
      await streamProjectReview(checkId, setReview);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setRunning("");
    }
  };

  const verdict = review.match(/VERDICT:\s*(\w+)/)?.[1];
  const reviewBody = review.replace(/^\s*VERDICT:.*\n?/, "");

  return (
    <div className="project">
      <div className="card project-intro">
        <div className="card-label">
          <Icon name="book" size={12} /> {step.name} project
          {step.passed && <span className="pill good push-right">Checkpoint passed</span>}
        </div>
        <h3>{step.title}</h3>
        <p className="muted">
          Build this in your own project folder, in your editor. When you're done, run the checkpoint: hidden tests run
          against your code. When they pass, Claude reviews your structure and best practices.
        </p>
      </div>

      <div className="prose">
        <Markdown text={step.instructions} />
      </div>

      {step.has_check && (
        <div className="card check-card">
          <label className="dir-label" htmlFor="project-dir">
            Your project folder
          </label>
          <div className="dir-row">
            <input
              id="project-dir"
              className="text-input mono"
              value={dir}
              onChange={(e) => setDir(e.target.value)}
              spellCheck={false}
            />
            {dir !== savedDir && (
              <button className="btn small" onClick={saveDir}>
                Save
              </button>
            )}
          </div>
          <div className="run-bar">
            <button className="btn primary" onClick={runCheck} disabled={!!running}>
              {running ? <span className="spinner" /> : <Icon name="play" size={13} />}
              {running === "tests" ? "Running checkpoint…" : running === "review" ? "Claude is reviewing…" : "Check my project"}
            </button>
            <button
              className="btn"
              onClick={() =>
                onAskClaude(
                  `I'm working on the ${step.name} project step "${step.title}".` +
                    (check && !check.passed ? `\n\nThe checkpoint failed:\n\n\`\`\`\n${check.output.slice(-1500)}\n\`\`\`` : "") +
                    "\n\nGive me a hint about what to do next (not the full code).",
                )
              }
            >
              <Icon name="sparkle" size={13} /> Ask Claude for help
            </button>
            {running === "tests" && <span className="muted small-text">First run may take a minute while uv installs packages.</span>}
          </div>
        </div>
      )}

      {error && <p className="error">{error}</p>}

      {check && (
        <div className="card result">
          <div className="result-head">
            <span className={`pill ${check.passed ? "good" : "bad"}`}>
              <Icon name={check.passed ? "check" : "x"} size={12} />
              {check.passed ? "Checkpoint passed" : "Checkpoint failed"}
            </span>
            <span className="muted">
              {check.summary} · {check.seconds.toFixed(1)}s
            </span>
          </div>
          {!check.passed && <FailureCards failures={check.failures} />}
          <details open={!check.passed && !check.failures?.length}>
            <summary>Full pytest output</summary>
            <pre className="term">{check.output || "(no output)"}</pre>
          </details>
          <div className="review">
            <div className="review-head">
              <span className="claude-mark tiny">
                <Icon name="sparkle" size={10} />
              </span>
              Claude code review
              <span className={`pill ${verdict ? (VERDICT_KIND[verdict] ?? "neutral") : "neutral"}`}>
                {verdict ? verdict.toLowerCase() : running === "review" ? "reviewing…" : "—"}
              </span>
            </div>
            {reviewBody ? (
              <Markdown text={reviewBody} />
            ) : !running && !check.passed ? (
              <button className="btn small" onClick={() => requestReview(check.check_id)}>
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
