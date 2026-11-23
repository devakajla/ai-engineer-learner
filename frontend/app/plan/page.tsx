"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { hm, Mark, niceDate, taskHref, TrackTag } from "@/components/PlanBits";
import { api, Roadmap, RoadmapDay, RoadmapTask } from "@/lib/api";

type DayState = "done" | "part" | "missed" | "today" | "future";

function dayState(d: RoadmapDay, today: string): DayState {
  const done = d.tasks.filter((t) => t.done).length;
  if (d.date > today) return "future";
  if (done === d.tasks.length) return "done";
  if (d.date === today) return "today";
  return done > 0 ? "part" : "missed";
}

export default function PlanPage() {
  const [rm, setRm] = useState<Roadmap | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    api.roadmap(new URLSearchParams(window.location.search).get("on")).then(setRm).catch((e) => setError(e.message));
  }, []);

  const weeks = useMemo(() => {
    if (!rm) return [];
    const out: { n: number; days: RoadmapDay[] }[] = [];
    // Week 1 = Mon 23 Nov. Day 1 (Sun 22 Nov) is the orientation day, shown before week 1.
    rm.days.forEach((d, i) => {
      const w = i === 0 ? 0 : Math.floor((i - 1) / 7) + 1;
      (out[w] ??= { n: w, days: [] }).days.push(d);
    });
    return out;
  }, [rm]);

  const byTrack = useMemo(() => {
    if (!rm) return [];
    const m = new Map<string, { label: string; total: number; done: number; minutes: number }>();
    for (const d of rm.days)
      for (const t of d.tasks) {
        const key = t.track_label ?? "Review";
        const e = m.get(key) ?? { label: key, total: 0, done: 0, minutes: 0 };
        e.total += 1;
        e.done += t.done ? 1 : 0;
        e.minutes += t.minutes;
        m.set(key, e);
      }
    return [...m.values()];
  }, [rm]);

  if (error) return <div className="center-msg error">{error}</div>;
  if (!rm) return <div className="center-msg">Loading…</div>;

  const todayWeek = weeks.findIndex((w) => w.days.some((d) => d.date === rm.today));
  const totalMinutes = rm.days.reduce((n, d) => n + d.tasks.reduce((a, t) => a + t.minutes, 0), 0);
  // Heatmap: columns are weeks (Mon..Sun rows); the first day (a Sunday) sits in its own first column.
  const cells = rm.days.map((d, i) => ({ d, col: i === 0 ? 0 : Math.floor((i - 1) / 7) + 1, row: (new Date(d.date + "T00:00:00").getDay() + 6) % 7 }));

  return (
    <main className="plan-page">
      <Link href="/" className="btn ghost small">← Today</Link>
      <h1>{rm.title}</h1>
      <p className="muted">
        {niceDate(rm.start!, true)} to {niceDate(rm.end!, true)} · {rm.total_days} days · about {Math.round(totalMinutes / 60)} hours.
        The plan is fixed. Skipped work stays overdue.
      </p>

      <section className="card">
        <div className="card-label">Every day</div>
        <div className="heat" style={{ gridTemplateColumns: `repeat(${weeks.length}, 1fr)` }}>
          {cells.map(({ d, col, row }) => (
            <div
              key={d.date}
              className={`heat-cell ${dayState(d, rm.today)}`}
              style={{ gridColumn: col + 1, gridRow: row + 1 }}
              title={`${niceDate(d.date)}: ${d.tasks.filter((t) => t.done).length}/${d.tasks.length} done`}
            />
          ))}
        </div>
        <div className="heat-legend">
          <span><i className="heat-cell done" /> all done</span>
          <span><i className="heat-cell part" /> partly</span>
          <span><i className="heat-cell missed" /> missed</span>
          <span><i className="heat-cell today" /> today</span>
          <span><i className="heat-cell future" /> coming</span>
        </div>
      </section>

      <section className="card">
        <div className="card-label">By topic</div>
        <div className="track-bars">
          {byTrack.map((t) => (
            <div key={t.label} className="track-bar">
              <div className="track-bar-top">
                <strong>{t.label}</strong>
                <span className="muted">{t.done}/{t.total} tasks · {Math.round(t.minutes / 60)} h</span>
              </div>
              <div className="meter"><div style={{ width: `${(100 * t.done) / t.total}%` }} /></div>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <div className="card-label">Week by week</div>
        {weeks.map((w, i) => {
          const tasks = w.days.flatMap((d) => d.tasks);
          const main = [...new Set(tasks.filter((t) => t.kind === "practise" && t.track !== "dsa").map((t) => t.track_label))];
          return (
            <details key={w.n} open={i === todayWeek} className="week">
              <summary>
                <strong>{w.n === 0 ? "Day 1" : `Week ${w.n}`}</strong>
                <span className="muted"> · {niceDate(w.days[0].date)} to {niceDate(w.days[w.days.length - 1].date)}</span>
                <span className="week-topics">{main.join(" + ")}</span>
                <span className="muted push-right">{tasks.filter((t) => t.done).length}/{tasks.length}</span>
              </summary>
              {w.days.map((d) => (
                <div key={d.date} className={`plan-day ${d.date === rm.today ? "is-today" : ""}`}>
                  <div className="plan-day-date">
                    {niceDate(d.date)}
                    <span className="muted">{hm(d.tasks.reduce((n, t) => n + t.minutes, 0))}</span>
                  </div>
                  <ul className="plan-rows tight">
                    {d.tasks.map((t: RoadmapTask) => {
                      const href = taskHref(t);
                      return (
                        <li key={t.id} className={t.done ? "is-done" : d.date < rm.today ? "is-late" : ""}>
                          <Mark done={t.done} />
                          <TrackTag task={t} />
                          {href ? <Link href={href}>{t.title}</Link> : <span>{t.title}</span>}
                          {t.part && t.part[1] > 1 && <span className="muted">({t.part[0]}/{t.part[1]})</span>}
                          {t.lesson && !t.available && <span className="pill neutral">not written yet</span>}
                          <span className="muted push-right">{hm(t.minutes)}</span>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ))}
            </details>
          );
        })}
      </section>
    </main>
  );
}
