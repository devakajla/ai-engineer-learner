"use client";

import { useState } from "react";
import { api, Lesson, QuizResult } from "@/lib/api";
import Icon from "./Icon";
import Markdown from "./Markdown";

type Props = {
  lesson: Lesson;
  onScored: (score: number, total: number) => void;
  onNext?: () => void; // go to Practice
};

const LETTERS = "ABCDEFGH";

export default function Quiz({ lesson, onScored, onNext }: Props) {
  const [chosen, setChosen] = useState<number[][]>(() => lesson.quiz.map(() => []));
  const [result, setResult] = useState<QuizResult | null>(null);
  const [error, setError] = useState("");

  const pick = (qi: number, oi: number, multi: boolean) => {
    if (result) return;
    setChosen((prev) =>
      prev.map((c, i) => {
        if (i !== qi) return c;
        if (!multi) return [oi];
        return c.includes(oi) ? c.filter((x) => x !== oi) : [...c, oi];
      }),
    );
  };

  const submit = async () => {
    setError("");
    try {
      const r = await api.submitQuiz(lesson.id, chosen);
      setResult(r);
      onScored(r.score, r.total);
      document.querySelector(".content")?.scrollTo({ top: 0, behavior: "smooth" });
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const retry = () => {
    setResult(null);
    setChosen(lesson.quiz.map(() => []));
  };

  const total = lesson.quiz.length;
  const answered = chosen.filter((c) => c.length > 0).length;
  const pct = result ? Math.round((100 * result.score) / result.total) : 0;
  const grade = result && (pct === 100 ? "good" : pct >= 50 ? "warn" : "bad");

  return (
    <div className="quiz">
      {result && (
        <div className={`score-card ${grade}`}>
          <div className="score-ring" style={{ "--pct": pct } as React.CSSProperties}>
            <span>{pct}%</span>
          </div>
          <div className="score-text">
            <strong>
              {result.score} of {result.total} correct
            </strong>
            <span className="muted">
              {grade === "good"
                ? "Perfect! You're ready for practice."
                : grade === "warn"
                  ? "Good. Read the explanations below for the ones you missed."
                  : "Re-read the theory, then try again."}
            </span>
          </div>
          <div className="score-actions">
            <button className="btn" onClick={retry}>
              <Icon name="reset" size={14} /> Retry
            </button>
            {onNext && (
              <button className="btn primary" onClick={onNext}>
                Practice <Icon name="arrowRight" size={14} />
              </button>
            )}
          </div>
        </div>
      )}

      {lesson.quiz.map((q, qi) => {
        const r = result?.results[qi];
        const multi = q.type === "multi";
        return (
          <div key={qi} className={`q-card ${r ? (r.correct ? "right" : "wrong") : ""}`}>
            <div className="q-meta">
              <span>
                Question {qi + 1} of {total}
              </span>
              {r ? (
                <span className={`pill ${r.correct ? "good" : "bad"}`}>{r.correct ? "Correct" : "Wrong"}</span>
              ) : (
                <span className="pill neutral">{multi ? "Select all that apply" : "Select one"}</span>
              )}
            </div>
            <div className="q-text">
              <Markdown text={q.q} />
            </div>
            <div className="options">
              {q.options.map((opt, oi) => {
                const isChosen = chosen[qi].includes(oi);
                const isAnswer = !!r?.answer.includes(oi);
                const state = r ? (isAnswer ? "is-answer" : isChosen ? "is-wrong" : "is-dim") : isChosen ? "is-chosen" : "";
                return (
                  <button
                    key={oi}
                    type="button"
                    className={`option ${state} ${multi ? "multi" : ""}`}
                    onClick={() => pick(qi, oi, multi)}
                    disabled={!!result}
                    aria-pressed={isChosen}
                  >
                    <span className="letter">
                      {r && isAnswer ? (
                        <Icon name="check" size={13} />
                      ) : r && isChosen ? (
                        <Icon name="x" size={13} />
                      ) : (
                        LETTERS[oi]
                      )}
                    </span>
                    <Markdown text={opt} inline />
                  </button>
                );
              })}
            </div>
            {r?.explain && (
              <div className="explain">
                <strong>Why: </strong>
                <Markdown text={r.explain} />
              </div>
            )}
          </div>
        );
      })}

      {!result && (
        <div className="quiz-footer">
          <div className="quiz-progress">
            <span>
              {answered}/{total} answered
            </span>
            <div className="meter">
              <div style={{ width: `${(100 * answered) / total}%` }} />
            </div>
          </div>
          {error && <span className="error">{error}</span>}
          <button className="btn primary" onClick={submit} disabled={answered < total}>
            Check answers
          </button>
        </div>
      )}
    </div>
  );
}
