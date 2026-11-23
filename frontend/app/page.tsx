"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { hm, Mark, niceDate, StepList, taskHref, TrackTag } from "@/components/PlanBits";
import Icon from "@/components/Icon";
import Markdown from "@/components/Markdown";
import { api, notifyProgress, Roadmap, RoadmapTask, streamGuide, streamPlanAsk } from "@/lib/api";

function whenLabel(t: RoadmapTask, today: string) {
  return t.date < today ? `from ${niceDate(t.date)}` : "";
}

/** The one thing to do now: the big card with the Start button. */
function NowCard({ task, today, onTick }: { task: RoadmapTask; today: string; onTick: (t: RoadmapTask) => void }) {
  const href = taskHref(task);
  const late = task.date < today;
  return (
    <section className={`card now-card ${late ? "late" : ""}`}>
      <div className="now-kicker">
        {late ? `Overdue, ${whenLabel(task, today)}` : "Do this now"}
        <span className="muted"> · {hm(task.minutes)}</span>
      </div>
      <div className="now-title-row">
        <TrackTag task={task} />
        <h2>{task.title}</h2>
        {task.part && task.part[1] > 1 && (
          <span className="muted">part {task.part[0]} of {task.part[1]}</span>
        )}
      </div>
      <StepList task={task} />
      {task.links && task.links.length > 0 && (
        <div className="plan-links">
          {task.links.map((l) => (
            <Link key={l.track + l.lesson} href={`/${l.track}/${l.lesson}?tab=quiz`} className="btn small">
              {l.title}
            </Link>
          ))}
        </div>
      )}
      <div className="now-actions">
        {href && (
          <Link href={href} className="btn primary big">
            {task.tab === "theory" ? "Start" : "Continue"} →
          </Link>
        )}
        {!task.gated && (
          <button className={`btn ${href ? "" : "primary"} big`} onClick={() => onTick(task)}>
            Mark done
          </button>
        )}
        {task.lesson && !task.available && (
          <span className="muted">Lesson not written yet{task.ready_by ? `, ready by ${niceDate(task.ready_by)}` : ""}.</span>
        )}
      </div>
    </section>
  );
}

/** Haiku's guidance: a short briefing for the plan, plus a box to ask about the plan or the task. */
function Guide({ on, stateKey, overdue }: { on: string | null; stateKey: string; overdue: boolean }) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [asking, setAsking] = useState(false);

  const brief = useCallback(
    (fresh = false) => {
      setBusy(true);
      streamGuide(setText, on, fresh)
        .catch(() => setText("Could not reach Claude. Check that you are logged in to the `claude` CLI."))
        .finally(() => setBusy(false));
    },
    [on],
  );
  // New briefing when the plan state changes (a task finished, a new day).
  useEffect(() => brief(), [brief, stateKey]);

  const ask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || asking) return;
    setAsking(true);
    setAnswer("");
    await streamPlanAsk(question, setAnswer, on).catch(() => setAnswer("Could not reach Claude."));
    setAsking(false);
  };

  return (
    <section className={`card guide ${overdue ? "late" : ""}`}>
      <div className="guide-head">
        <span className="card-label"><Icon name="sparkle" size={13} /> Guide</span>
        <button className="btn ghost small" onClick={() => brief(true)} disabled={busy} title="Write a new briefing">
          {busy ? <span className="spinner" /> : <Icon name="reset" size={13} />} Refresh
        </button>
      </div>
      <div className="guide-text">
        {text ? <Markdown text={text} /> : <span className="muted">Reading your plan…</span>}
      </div>
      <form className="guide-ask" onSubmit={ask}>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask about the plan or today's task…"
          aria-label="Ask the guide"
        />
        <button className="btn small" disabled={asking || !question.trim()}>{asking ? "…" : "Ask"}</button>
      </form>
      {answer && (
        <div className="guide-answer">
          <Markdown text={answer} />
        </div>
      )}
    </section>
  );
}

export default function Home() {
  const [rm, setRm] = useState<Roadmap | null>(null);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    api.roadmap(new URLSearchParams(window.location.search).get("on")).then(setRm).catch((e) => setError(e.message));
  }, []);
  useEffect(load, [load]);
  // Reload when you come back from a lesson tab, so the gates are fresh.
  useEffect(() => {
    window.addEventListener("focus", load);
    return () => window.removeEventListener("focus", load);
  }, [load]);

  const on = typeof window === "undefined" ? null : new URLSearchParams(window.location.search).get("on");

  const tick = async (t: RoadmapTask) => {
    await api.markTask(t.id, !t.done).catch((e) => setError(e.message));
    notifyProgress();
    load();
  };

  if (error) return <div className="center-msg error">{error}</div>;
  if (!rm) return <div className="center-msg">Loading…</div>;

  const queue = [...rm.overdue, ...rm.tasks.filter((t) => !t.done)];
  const now = queue[0];
  const rest = queue.slice(1);
  const doneToday = rm.tasks.filter((t) => t.done);
  const minutesLeft = queue.reduce((n, t) => n + t.minutes, 0);
  const tomorrow = rm.days.find((d) => d.date > rm.today);

  return (
    <main className="home">
      <header className="home-head">
        <div>
          <div className="muted">{niceDate(rm.today, true)}</div>
          <h1>
            {rm.state === "running" && `Day ${rm.day_number} of ${rm.total_days}`}
            {rm.state === "before" && `Plan starts ${niceDate(rm.start!)}`}
            {rm.state === "after" && "Plan finished"}
            {rm.state === "empty" && "No plan yet"}
          </h1>
        </div>
        <div className="home-stats">
          <div title="Days in a row with every task done">
            <strong>{rm.streak}</strong>
            <span>day streak</span>
          </div>
          <div title="Tasks done out of the tasks due so far">
            <strong>{rm.done_count}/{rm.due_count}</strong>
            <span>done</span>
          </div>
          <Link href="/plan" className="btn small">Full plan</Link>
        </div>
      </header>

      {rm.state === "empty" && (
        <p className="muted">Run <code>uv run python scripts/build_roadmap.py</code> to create the plan.</p>
      )}

      {rm.state === "running" && (
        <Guide
          on={on}
          overdue={rm.overdue.length > 0}
          stateKey={`${rm.today}|${rm.done_count}|${rm.overdue.length}`}
        />
      )}

      {now ? (
        <NowCard task={now} today={rm.today} onTick={tick} />
      ) : (
        rm.state === "running" && (
          <section className="card all-done">
            <h2>Done for today.</h2>
            <p className="muted">
              {rm.streak > 0 ? `Streak: ${rm.streak} ${rm.streak === 1 ? "day" : "days"}. ` : ""}
              {tomorrow && `Tomorrow (${niceDate(tomorrow.date)}): ${tomorrow.tasks.map((t) => t.title).join(", ")}.`}
            </p>
          </section>
        )
      )}

      {(rest.length > 0 || doneToday.length > 0) && (
        <section className="card">
          <div className="card-label">
            {rest.length > 0 ? `Then · ${hm(minutesLeft - (now?.minutes ?? 0))} left` : "Done today"}
          </div>
          <ul className="plan-rows">
            {rest.slice(0, 6).map((t) => {
              const href = taskHref(t);
              return (
                <li key={t.id}>
                  <Mark done={false} />
                  <TrackTag task={t} />
                  {href ? <Link href={href}>{t.title}</Link> : <span>{t.title}</span>}
                  {t.date < rm.today && <span className="pill bad">overdue</span>}
                  <span className="muted push-right">{hm(t.minutes)}</span>
                </li>
              );
            })}
            {rest.length > 6 && (
              <li className="muted">and {rest.length - 6} more, in order. Finish these first.</li>
            )}
            {doneToday.map((t) => (
              <li key={t.id} className="is-done">
                <Mark done />
                <TrackTag task={t} />
                <span>{t.title}</span>
                {!t.gated && (
                  <button className="btn ghost small push-right" onClick={() => tick(t)}>Undo</button>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
