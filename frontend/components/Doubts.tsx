"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { api, Doubt, DOUBTS_EVENT, notifyDoubts } from "@/lib/api";
import Icon from "./Icon";

/** Where a new doubt is being added: a label shown to the learner, plus a heading id to scroll back to. */
export type DoubtSpot = { location: string; anchor: string | null };

const when = (iso: string | null) =>
  iso ? new Date(iso + "Z").toLocaleDateString(undefined, { day: "numeric", month: "short" }) : "";

/** A small modal to star a spot as doubtful and write what was unclear. */
export function DoubtDialog({
  lessonId,
  spot,
  onSaved,
  onClose,
}: {
  lessonId: string;
  spot: DoubtSpot;
  onSaved: (d: Doubt) => void;
  onClose: () => void;
}) {
  const [location, setLocation] = useState(spot.location);
  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const noteRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    noteRef.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);

  const save = async () => {
    if (saving || !location.trim()) return;
    setSaving(true);
    setError("");
    try {
      onSaved(await api.addDoubt(lessonId, { location: location.trim(), anchor: spot.anchor, note }));
      notifyDoubts();
      onClose();
    } catch (e) {
      setError((e as Error).message);
      setSaving(false);
    }
  };

  return (
    <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <form
        className="modal doubt-dialog"
        role="dialog"
        aria-label="Mark a doubt"
        onSubmit={(e) => {
          e.preventDefault();
          save();
        }}
      >
        <div className="doubt-dialog-head">
          <span className="doubt-star-badge">
            <Icon name="star" size={16} filled />
          </span>
          <div>
            <strong>Mark a doubt</strong>
            <span className="muted">Starred spots show up in your revise list.</span>
          </div>
        </div>
        <label className="dir-label" htmlFor="doubt-where">
          Where
        </label>
        <input id="doubt-where" className="text-input" value={location} onChange={(e) => setLocation(e.target.value)} />
        <label className="dir-label" htmlFor="doubt-note">
          What was unclear?
        </label>
        <textarea
          id="doubt-note"
          ref={noteRef}
          className="text-input doubt-note-input"
          rows={4}
          placeholder="e.g. Why does a mutable default argument keep its value between calls?"
          value={note}
          onChange={(e) => setNote(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
              e.preventDefault();
              save();
            }
          }}
        />
        {error && <p className="error small-text">{error}</p>}
        <div className="doubt-dialog-actions">
          <span className="muted small-text">⌘↵ to save</span>
          <button type="button" className="btn ghost small" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" className="btn primary small" disabled={saving || !location.trim()}>
            <Icon name="star" size={13} filled /> Save doubt
          </button>
        </div>
      </form>
    </div>
  );
}

/** One doubt: where it came up, the note (editable), and resolve / delete actions. */
function DoubtItem({
  doubt,
  onChange,
  onGo,
}: {
  doubt: Doubt;
  onChange: (d: Doubt | null) => void;
  onGo: (d: Doubt) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [note, setNote] = useState(doubt.note);

  const update = async (body: { note?: string; resolved?: boolean }) => {
    onChange(await api.updateDoubt(doubt.id, body));
    notifyDoubts();
  };
  const remove = async () => {
    if (!confirm("Delete this doubt?")) return;
    await api.deleteDoubt(doubt.id);
    onChange(null);
    notifyDoubts();
  };

  return (
    <li className={`doubt-item ${doubt.resolved ? "resolved" : ""}`}>
      <div className="doubt-item-head">
        <button className="doubt-where" onClick={() => onGo(doubt)} title="Go to this spot">
          <Icon name="star" size={12} filled={!doubt.resolved} /> {doubt.location}
        </button>
        <span className="muted small-text">{when(doubt.created_at)}</span>
        <span className="doubt-actions">
          <button
            className="icon-btn small"
            onClick={() => update({ resolved: !doubt.resolved })}
            title={doubt.resolved ? "Mark as still unclear" : "Revised — mark as clear"}
          >
            <Icon name={doubt.resolved ? "reset" : "check"} size={14} />
          </button>
          <button className="icon-btn small" onClick={() => setEditing((e) => !e)} title="Edit note">
            <Icon name="edit" size={14} />
          </button>
          <button className="icon-btn small" onClick={remove} title="Delete">
            <Icon name="trash" size={14} />
          </button>
        </span>
      </div>
      {editing ? (
        <div className="doubt-edit">
          <textarea
            className="text-input doubt-note-input"
            rows={3}
            value={note}
            onChange={(e) => setNote(e.target.value)}
            autoFocus
          />
          <div className="doubt-dialog-actions">
            <button className="btn ghost small" onClick={() => setEditing(false)}>
              Cancel
            </button>
            <button className="btn primary small" onClick={() => update({ note }).then(() => setEditing(false))}>
              Save
            </button>
          </div>
        </div>
      ) : (
        doubt.note && <p className="doubt-note">{doubt.note}</p>
      )}
    </li>
  );
}

/** The lesson's doubts, shown above the tabs so they are the first thing you see when revising. */
export function DoubtList({
  doubts,
  onChange,
  onGo,
}: {
  doubts: Doubt[];
  onChange: (doubts: Doubt[]) => void;
  onGo: (d: Doubt) => void;
}) {
  const [showResolved, setShowResolved] = useState(false);
  if (!doubts.length) return null;
  const open = doubts.filter((d) => !d.resolved);
  const resolved = doubts.filter((d) => d.resolved);
  const shown = showResolved ? [...open, ...resolved] : open;

  const replace = (id: number, d: Doubt | null) =>
    onChange(d ? doubts.map((x) => (x.id === id ? d : x)) : doubts.filter((x) => x.id !== id));

  return (
    <div className="card doubt-list" id="doubts">
      <div className="doubt-list-head">
        <span className="card-label">
          <Icon name="star" size={13} filled /> {open.length ? `${open.length} to revise` : "All doubts revised"}
        </span>
        {resolved.length > 0 && (
          <button className="btn ghost small" onClick={() => setShowResolved((s) => !s)}>
            {showResolved ? "Hide revised" : `Show revised (${resolved.length})`}
          </button>
        )}
      </div>
      {shown.length > 0 && (
        <ul>
          {shown.map((d) => (
            <DoubtItem key={d.id} doubt={d} onChange={(n) => replace(d.id, n)} onGo={onGo} />
          ))}
        </ul>
      )}
    </div>
  );
}

/** Top bar button: every open doubt across all lessons, to pick what to revise next. */
export function ReviseMenu() {
  const [doubts, setDoubts] = useState<Doubt[]>([]);
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const load = () =>
      api
        .doubts()
        .then(setDoubts)
        .catch(() => {});
    load();
    window.addEventListener(DOUBTS_EVENT, load);
    return () => window.removeEventListener(DOUBTS_EVENT, load);
  }, []);

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => !ref.current?.contains(e.target as Node) && setOpen(false);
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("mousedown", onClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <div className="model-menu" ref={ref}>
      <button
        className={`btn small ghost model-btn ${open ? "on" : ""}`}
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        title="Doubts to revise"
      >
        <Icon name="star" size={14} filled={doubts.length > 0} className={doubts.length ? "star-on" : ""} />
        Revise{doubts.length > 0 && <span className="revise-count">{doubts.length}</span>}
      </button>
      {open && (
        <div className="model-pop revise-pop">
          <div className="model-pop-head">
            <strong>Doubts to revise</strong>
            <span>Star a heading or use “Mark doubt” in any lesson.</span>
          </div>
          {doubts.length === 0 ? (
            <p className="revise-empty muted">No open doubts. Nice!</p>
          ) : (
            <ul className="revise-list">
              {doubts.map((d) => (
                <li key={d.id}>
                  <Link href={`/${d.track}/${d.slug}#${d.anchor ?? "doubts"}`} onClick={() => setOpen(false)}>
                    <span className="revise-lesson">{d.lesson_title}</span>
                    <span className="revise-where">
                      <Icon name="star" size={11} filled /> {d.location}
                    </span>
                    {d.note && <span className="revise-note">{d.note}</span>}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
