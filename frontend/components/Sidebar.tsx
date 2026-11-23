"use client";

import Link from "next/link";
import { TrackDetail } from "@/lib/api";
import { usePref } from "@/lib/prefs";
import Icon from "./Icon";

/** "Level 1 — Foundations (fast-track)" -> ["Level 1", "Foundations (fast-track)"] */
function splitLevel(title: string): [string, string] {
  const [a, b] = title.split("—").map((s) => s.trim());
  return b ? [a, b] : ["", a];
}

export default function Sidebar({
  track,
  currentId,
  onClose,
}: {
  track: TrackDetail;
  currentId: string;
  onClose: () => void;
}) {
  // Remembered open/closed state per level; the level holding the current lesson is open unless closed explicitly.
  const [levelState, setLevelState] = usePref<Record<string, boolean>>(`levels.${track.id}`, {});
  let number = 0;

  return (
    <aside className="sidebar">
      <div className="sidebar-head">
        <div className="sidebar-title">
          <h2>{track.title}</h2>
          <button className="icon-btn small" onClick={onClose} title="Hide lessons (⌘B)">
            <Icon name="sidebar" size={15} />
          </button>
        </div>
        <div className="meter">
          <div style={{ width: `${track.percent}%` }} />
        </div>
        <small className="muted">
          {track.done} of {track.total} lessons done · {track.percent}%
        </small>
      </div>

      <nav className="levels">
        {track.levels.map((level) => {
          const [tag, name] = splitLevel(level.title);
          const hasCurrent = level.lessons.some((l) => l.id === currentId);
          const open = levelState[level.id] ?? hasCurrent;
          const done = level.lessons.filter((l) => l.status === "done").length;
          const startNumber = number;
          number += level.lessons.length;
          return (
            <section key={level.id} className={`level ${open ? "open" : ""}`}>
              <button
                className="level-head"
                onClick={() => setLevelState((s) => ({ ...s, [level.id]: !open }))}
                aria-expanded={open}
              >
                <Icon name="chevronRight" size={14} className="chev" />
                <span className="level-text">
                  {tag && <span className="level-tag">{tag}</span>}
                  <span className="level-name">{name}</span>
                </span>
                <span className="level-count">
                  {done}/{level.lessons.length}
                </span>
              </button>
              {open && (
                <div className="level-lessons">
                  {level.lessons.map((l, i) => {
                    const n = startNumber + i + 1;
                    const isCurrent = l.id === currentId;
                    const isNext = track.next_up?.id === l.id && !isCurrent;
                    const body = (
                      <>
                        <span className={`st ${l.available ? l.status : "soon"}`}>
                          {!l.available ? (
                            <Icon name="lock" size={11} />
                          ) : l.status === "done" ? (
                            <Icon name="check" size={12} />
                          ) : (
                            n
                          )}
                        </span>
                        <span className="lesson-title">{l.title}</span>
                        {l.doubts > 0 && (
                          <span
                            className="lesson-doubt"
                            title={`${l.doubts} doubt${l.doubts > 1 ? "s" : ""} to revise`}
                          >
                            <Icon name="star" size={12} filled />
                            {l.doubts > 1 && l.doubts}
                          </span>
                        )}
                        {l.kind === "interview" && <span className="tag">Interview</span>}
                        {isNext && <span className="tag accent">Next</span>}
                      </>
                    );
                    return l.available ? (
                      <Link
                        key={l.id}
                        href={`/${track.id}/${l.slug}`}
                        className={`lesson-link ${isCurrent ? "current" : ""}`}
                      >
                        {body}
                      </Link>
                    ) : (
                      <span key={l.id} className="lesson-link soon" title="Coming soon">
                        {body}
                      </span>
                    );
                  })}
                </div>
              )}
            </section>
          );
        })}
      </nav>
    </aside>
  );
}
