"use client";

import Link from "next/link";
import { RoadmapTask } from "@/lib/api";
import Icon from "./Icon";

export function niceDate(iso: string, long = false) {
  return new Date(iso + "T00:00:00").toLocaleDateString("en-GB", {
    weekday: "short",
    day: "numeric",
    month: "short",
    ...(long ? { year: "numeric" } : {}),
  });
}

export function hm(minutes: number) {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h ? (m ? `${h} h ${m} min` : `${h} h`) : `${m} min`;
}

export function taskHref(t: RoadmapTask) {
  if (!t.lesson || !t.available || !t.track) return null;
  return `/${t.track}/${t.lesson}${t.tab && t.tab !== "theory" ? `?tab=${t.tab}` : ""}`;
}

/** Round status mark: filled green = done, hollow = open. */
export function Mark({ done }: { done: boolean }) {
  return (
    <span className={`plan-mark ${done ? "done" : ""}`} aria-hidden>
      {done && <Icon name="check" size={13} />}
    </span>
  );
}

/** The steps of a task, each with its live status (quiz score, exercises solved, project). */
export function StepList({ task }: { task: RoadmapTask }) {
  const g = task.gate;
  return (
    <ol className="plan-steps">
      {task.steps.map((text, i) => {
        let status: "done" | "open" | "none" = "none";
        let note = "";
        if (g?.quiz && text.startsWith("Quiz")) {
          status = g.quiz.ok ? "done" : "open";
          note = g.quiz.best !== null ? `best ${g.quiz.best}%` : "";
        } else if (g?.exercises && text.startsWith("Exercises")) {
          status = g.exercises.ok ? "done" : "open";
          note = `${g.exercises.solved}/${g.exercises.total} passed`;
        } else if (g?.bonus && text.startsWith("Bonus")) {
          status = g.bonus.solved === g.bonus.total ? "done" : "none";
          note = `bonus ${g.bonus.solved}/${g.bonus.total}`;
        } else if (g?.project && text.startsWith("Project")) {
          status = g.project.ok ? "done" : "open";
        }
        return (
          <li key={i} className={status}>
            <Mark done={status === "done"} />
            <span>{text}</span>
            {note && <span className="plan-step-note">{note}</span>}
          </li>
        );
      })}
    </ol>
  );
}

export function TrackTag({ task }: { task: RoadmapTask }) {
  return <span className="tag accent">{task.track_label ?? (task.kind === "review" ? "Review" : "")}</span>;
}
