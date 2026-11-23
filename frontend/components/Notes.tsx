"use client";

import { useEffect, useRef, useState } from "react";
import { api, NoteState, streamNotes } from "@/lib/api";
import Icon from "./Icon";
import Markdown from "./Markdown";

type Mode = "view" | "edit" | "generating" | "preview";

const when = (iso: string | null) =>
  iso ? new Date(iso + "Z").toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" }) : "";

/**
 * The lesson's revision note. Opens either to read the saved note, or straight into
 * "Make notes" / "Update notes": Claude streams a draft that merges the old note with the new
 * chat, and nothing is saved until the learner presses Save.
 */
export function NotesDialog({
  lessonId,
  lessonTitle,
  note,
  generate,
  onSaved,
  onClose,
}: {
  lessonId: string;
  lessonTitle: string;
  note: NoteState;
  generate: boolean; // start drafting as soon as the dialog opens
  onSaved: (n: NoteState) => void;
  onClose: () => void;
}) {
  const [mode, setMode] = useState<Mode>(generate ? "generating" : "view");
  const [saved, setSaved] = useState(note);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [justSaved, setJustSaved] = useState(false);
  const cursor = useRef(note.latest_chat_id); // the chat the current draft covers
  const abortRef = useRef<AbortController | null>(null);

  const draftNote = async () => {
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    setMode("generating");
    setJustSaved(false);
    setError("");
    setDraft("");
    try {
      // Re-read the note first: chat may have moved on since the page loaded.
      const fresh = await api.note(lessonId);
      setSaved(fresh);
      cursor.current = fresh.latest_chat_id;
      const text = await streamNotes(lessonId, fresh.latest_chat_id, setDraft, ctrl.signal);
      if (text.startsWith("Claude is not available")) throw new Error(text);
      if (!text.trim()) throw new Error("Claude returned an empty note. Try again.");
      setMode("preview");
    } catch (e) {
      if (ctrl.signal.aborted) return;
      setError((e as Error).message);
      setMode("view");
    }
  };

  useEffect(() => {
    if (generate) draftNote();
    return () => abortRef.current?.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && mode !== "generating" && onClose();
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose, mode]);

  const save = async (body: string) => {
    if (saving || !body.trim()) return;
    setSaving(true);
    setError("");
    try {
      const n = await api.saveNote(lessonId, body, cursor.current);
      setSaved(n);
      onSaved(n);
      setJustSaved(true);
      setMode("view");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const stop = () => {
    abortRef.current?.abort();
    setMode("view");
  };

  const title = mode === "view" || mode === "edit" ? "Notes" : saved.exists ? "Update notes" : "Make notes";

  return (
    <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && mode !== "generating" && onClose()}>
      <div className="modal notes-dialog" role="dialog" aria-label={title}>
        <div className="doubt-dialog-head">
          <span className="doubt-star-badge notes-badge">
            <Icon name="book" size={16} />
          </span>
          <div>
            <strong>
              {title} · {lessonTitle}
            </strong>
            <span className="muted">
              {mode === "generating" && "Claude is writing. Nothing is saved yet."}
              {mode === "preview" && "Check the draft, then save it. Your old note stays until you do."}
              {(mode === "view" || mode === "edit") &&
                (saved.exists ? (justSaved ? "Saved ✓" : `Saved ${when(saved.updated_at)}`) : "No note for this lesson yet.")}
            </span>
          </div>
          <button className="icon-btn small notes-close" onClick={onClose} title="Close" disabled={mode === "generating"}>
            <Icon name="x" size={14} />
          </button>
        </div>

        <div className="notes-body">
          {mode === "edit" ? (
            <textarea
              className="text-input notes-editor"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              spellCheck={false}
              autoFocus
            />
          ) : mode === "generating" || mode === "preview" ? (
            draft ? (
              <div className="prose">
                <Markdown text={draft} />
              </div>
            ) : (
              <p className="muted">Reading the lesson and your chat…</p>
            )
          ) : saved.exists ? (
            <div className="prose">
              <Markdown text={saved.body} />
            </div>
          ) : (
            <p className="muted">
              Press “Make notes”. Claude writes the key code of this lesson and answers the confusions you had in chat.
            </p>
          )}
        </div>

        {error && <p className="error small-text">{error}</p>}

        <div className="doubt-dialog-actions">
          {mode === "view" && saved.has_new_chat && saved.exists && (
            <span className="muted small-text">You chatted after the last save.</span>
          )}
          {mode === "generating" && (
            <button className="btn ghost small" onClick={stop}>
              <Icon name="stop" size={13} /> Stop
            </button>
          )}
          {mode === "preview" && (
            <>
              <button className="btn ghost small" onClick={() => setMode("view")}>
                Discard
              </button>
              <button className="btn small" onClick={draftNote}>
                <Icon name="reset" size={13} /> Redo
              </button>
              <button
                className="btn small"
                onClick={() => {
                  setMode("edit");
                }}
              >
                <Icon name="edit" size={13} /> Edit first
              </button>
              <button className="btn primary small" onClick={() => save(draft)} disabled={saving}>
                Save notes
              </button>
            </>
          )}
          {mode === "edit" && (
            <>
              <button className="btn ghost small" onClick={() => setMode("view")}>
                Cancel
              </button>
              <button className="btn primary small" onClick={() => save(draft)} disabled={saving || !draft.trim()}>
                Save notes
              </button>
            </>
          )}
          {mode === "view" && (
            <>
              {saved.exists && (
                <button
                  className="btn ghost small"
                  onClick={() => {
                    setDraft(saved.body);
                    setMode("edit");
                  }}
                >
                  <Icon name="edit" size={13} /> Edit
                </button>
              )}
              {/* Not the primary button, and "Done" sits where "Save notes" was, so a double-click on Save can't start a new draft. */}
              <button className={`btn small ${saved.exists ? "" : "primary"}`} onClick={draftNote}>
                <Icon name="sparkle" size={13} /> {saved.exists ? "Update with Claude" : "Make notes"}
              </button>
              {saved.exists && (
                <button className="btn primary small" onClick={onClose}>
                  Done
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
