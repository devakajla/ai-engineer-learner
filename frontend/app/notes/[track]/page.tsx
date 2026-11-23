"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import Icon from "@/components/Icon";
import Markdown from "@/components/Markdown";
import { api, notesExportUrl, TrackNotes } from "@/lib/api";

type Level = TrackNotes["levels"][number];
type Lesson = Level["lessons"][number];
// One lesson at a time, or every note of one module stacked.
type Pick = { kind: "lesson"; slug: string } | { kind: "level"; id: string };

/** Revision notes of a track: pick a module, then read one lesson at a time or the whole module. */
export default function NotesPage() {
  const { track } = useParams<{ track: string }>();
  const [data, setData] = useState<TrackNotes | null>(null);
  const [error, setError] = useState("");
  const [pick, setPick] = useState<Pick | null>(null);

  useEffect(() => {
    let stale = false;
    api
      .trackNotes(track)
      .then((d) => {
        if (stale) return;
        setData(d);
        // Open the lesson from the URL hash, else the first lesson that has a note.
        const all = d.levels.flatMap((lv) => lv.lessons.filter((l) => l.available));
        const hash = decodeURIComponent(window.location.hash.slice(1));
        const first = all.find((l) => l.slug === hash) ?? all.find((l) => l.note) ?? all[0];
        if (first) setPick({ kind: "lesson", slug: first.slug });
      })
      .catch((e) => !stale && setError(e.message));
    return () => {
      stale = true;
    };
  }, [track]);

  const lessons = useMemo(
    () => (data ? data.levels.flatMap((lv) => lv.lessons.filter((l) => l.available)) : []),
    [data],
  );

  const choose = (p: Pick) => {
    setPick(p);
    window.history.replaceState(null, "", p.kind === "lesson" ? `#${p.slug}` : window.location.pathname);
    window.scrollTo({ top: 0 });
  };

  if (error) return <div className="center-msg error">{error}</div>;
  if (!data) return <div className="center-msg">Loading…</div>;

  const total = lessons.filter((l) => l.note).length;
  const current = pick?.kind === "lesson" ? lessons.find((l) => l.slug === pick.slug) : undefined;
  const level = pick?.kind === "level" ? data.levels.find((lv) => lv.id === pick.id) : undefined;
  const index = current ? lessons.indexOf(current) : -1;

  const noteOf = (l: Lesson) =>
    l.note ? <Markdown text={l.note.body} /> : <p className="muted">No notes yet for this lesson.</p>;

  return (
    <main className="notes-page">
      <div className="notes-page-head">
        <div>
          <h1>{data.title} notes</h1>
          <span className="muted">{total ? `${total} of ${lessons.length} lessons have notes` : "No notes yet"}</span>
        </div>
        <div className="notes-page-actions">
          <Link className="btn small" href={current ? `/${track}/${current.slug}` : `/${track}`}>
            <Icon name="arrowLeft" size={14} /> {current ? "Back to this lesson" : "Back to lessons"}
          </Link>
          {total > 0 && (
            <a className="btn small" href={notesExportUrl(track)} download>
              Download .md
            </a>
          )}
        </div>
      </div>

      {total === 0 && (
        <p className="muted">
          Open a lesson and press “Make notes” at the bottom, next to “Mark lesson as done”. Notes you save show up here by module.
        </p>
      )}

      <div className="notes-layout">
        <nav className="notes-nav" aria-label="Modules and lessons">
          {data.levels.map((lv) => {
            const items = lv.lessons.filter((l) => l.available);
            if (!items.length) return null;
            const noted = items.filter((l) => l.note).length;
            return (
              <div key={lv.id} className="notes-nav-group">
                <button
                  className={`notes-nav-level ${level?.id === lv.id ? "active" : ""}`}
                  onClick={() => choose({ kind: "level", id: lv.id })}
                  title="Read every note of this module"
                >
                  <span className="notes-nav-level-title">{lv.title}</span>
                  <span className={`notes-nav-count ${noted === items.length ? "full" : ""}`}>
                    {noted}/{items.length}
                  </span>
                </button>
                {items.map((l) => (
                  <button
                    key={l.id}
                    className={`notes-nav-lesson ${current?.id === l.id ? "active" : ""} ${l.note ? "" : "empty"}`}
                    onClick={() => choose({ kind: "lesson", slug: l.slug })}
                  >
                    <span className={`notes-nav-dot ${l.note ? "on" : ""}`} />
                    {l.title}
                  </button>
                ))}
              </div>
            );
          })}
        </nav>

        <section className="notes-view">
          {current && (
            <>
              <div className="notes-lesson-head">
                <strong>{current.title}</strong>
                <Link className="btn small primary" href={`/${track}/${current.slug}`}>
                  Open lesson: theory, quiz, practice <Icon name="arrowRight" size={13} />
                </Link>
              </div>
              <div className="card notes-card">{noteOf(current)}</div>
              <div className="notes-pager">
                <button
                  className="btn small ghost"
                  disabled={index <= 0}
                  onClick={() => choose({ kind: "lesson", slug: lessons[index - 1].slug })}
                >
                  <Icon name="arrowLeft" size={13} /> {index > 0 ? lessons[index - 1].title : "Previous"}
                </button>
                <button
                  className="btn small ghost"
                  disabled={index >= lessons.length - 1}
                  onClick={() => choose({ kind: "lesson", slug: lessons[index + 1].slug })}
                >
                  {index < lessons.length - 1 ? lessons[index + 1].title : "Next"} <Icon name="arrowRight" size={13} />
                </button>
              </div>
            </>
          )}

          {level && (
            <>
              <div className="notes-lesson-head">
                <strong>{level.title}</strong>
                <span className="muted">whole module</span>
              </div>
              {level.lessons
                .filter((l) => l.available)
                .map((l) => (
                  <div key={l.id} className="card notes-card">
                    <div className="notes-lesson-head">
                      <strong>{l.title}</strong>
                      <Link href={`/${track}/${l.slug}`}>Open lesson</Link>
                    </div>
                    {noteOf(l)}
                  </div>
                ))}
            </>
          )}
        </section>
      </div>
    </main>
  );
}
