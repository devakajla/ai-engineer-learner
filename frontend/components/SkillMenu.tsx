"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { TrackSummary } from "@/lib/api";
import Icon from "./Icon";

/** Compact dropdown to switch skill (track). Mouse or keyboard: ↑/↓ to move, Enter to pick, Esc to close. */
export default function SkillMenu({ tracks, current }: { tracks: TrackSummary[]; current?: string }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [focus, setFocus] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const activeIndex = Math.max(0, tracks.findIndex((t) => t.id === current));
  const active = tracks[activeIndex];

  useEffect(() => {
    if (!open) return;
    setFocus(activeIndex);
    const onClick = (e: MouseEvent) => !ref.current?.contains(e.target as Node) && setOpen(false);
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open, activeIndex]);

  const choose = (t: TrackSummary) => {
    setOpen(false);
    if (t.id !== current) router.push(`/${t.id}`);
  };

  const onKey = (e: React.KeyboardEvent) => {
    if (!open) {
      if (e.key === "ArrowDown" || e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        setOpen(true);
      }
      return;
    }
    if (e.key === "Escape") setOpen(false);
    else if (e.key === "ArrowDown") setFocus((f) => (f + 1) % tracks.length);
    else if (e.key === "ArrowUp") setFocus((f) => (f - 1 + tracks.length) % tracks.length);
    else if (e.key === "Enter") choose(tracks[focus]);
    else return;
    e.preventDefault();
  };

  if (!active) return null;

  return (
    <div className="skill-menu" ref={ref} onKeyDown={onKey}>
      <button
        className={`skill-btn ${open ? "open" : ""}`}
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="listbox"
        aria-expanded={open}
        title="Switch skill"
      >
        <span className="skill-badge">{active.title[0]}</span>
        <span className="skill-name">{active.title}</span>
        <Icon name="chevronDown" size={14} className="skill-chev" />
      </button>

      {open && (
        <ul className="skill-pop" role="listbox" aria-label="Skills">
          {tracks.map((t, i) => (
            <li
              key={t.id}
              role="option"
              aria-selected={t.id === active.id}
              className={`skill-option ${i === focus ? "focused" : ""} ${t.id === active.id ? "selected" : ""}`}
              onMouseEnter={() => setFocus(i)}
              onClick={() => choose(t)}
            >
              <span className="skill-badge">{t.title[0]}</span>
              <span className="skill-option-body">
                <span className="skill-option-name">{t.title}</span>
                <span className="skill-option-sub">
                  {t.done}/{t.total} done · {t.percent}%
                </span>
              </span>
              {t.id === active.id && <Icon name="check" size={16} className="skill-check" />}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
