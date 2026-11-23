"use client";

import { useEffect, useRef, useState } from "react";
import { AISettings, AIUse, api } from "@/lib/api";
import Icon from "./Icon";

// How each model and effort level is described in the menu. `usage` is 1–3 bars.
const MODELS: Record<string, { desc: string; usage: number }> = {
  "claude-haiku-5-5": { desc: "Fastest and lightest. Good for reviews and quick questions.", usage: 1 },
  "claude-sonnet-5-5": { desc: "Great quality for lessons and explanations.", usage: 2 },
  "claude-opus-5-5": { desc: "Strongest, for when you're really stuck.", usage: 3 },
};

const EFFORTS: Record<string, string> = {
  low: "Quick answers with little thinking. Lightest on usage.",
  medium: "Balanced thinking. A good default.",
  high: "Thinks more before answering. Uses more.",
  xhigh: "Deep thinking for hard problems. Uses a lot.",
  max: "Thinks as long as it needs. Heaviest on usage.",
};

const USES: { id: AIUse; label: string; desc: string }[] = [
  { id: "chat", label: "Chat", desc: "Lesson chat with your tutor." },
  { id: "review", label: "Reviews", desc: "Exercise and project reviews." },
];

function UsageBars({ level }: { level: number }) {
  return (
    <span className={`usage-bars ${level === 3 ? "high" : ""}`} title={`Usage: ${["low", "medium", "high"][level - 1]}`}>
      {[1, 2, 3].map((n) => (
        <i key={n} className={n <= level ? "lit" : ""} />
      ))}
    </span>
  );
}

/** Picks the Claude model and effort, separately for chat and for reviews. Saved on the backend. */
export default function ModelMenu() {
  const [ai, setAI] = useState<AISettings | null>(null);
  const [open, setOpen] = useState(false);
  const [use, setUse] = useState<AIUse>("chat");
  const [error, setError] = useState("");
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.aiSettings().then(setAI).catch(() => {});
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

  if (!ai) return null;

  const current = ai[use];
  const save = (change: { model?: string; effort?: string }) => {
    setAI({ ...ai, [use]: { ...current, ...change } }); // feels instant; the server reply confirms it
    setError("");
    api
      .setAISettings({ use, ...change })
      .then(setAI)
      .catch((e) => setError((e as Error).message));
  };

  const label = (id: string) => ai.models.find((m) => m.id === id)?.label ?? id;

  return (
    <div className="model-menu" ref={ref}>
      <button
        className={`btn small ghost model-btn ${open ? "on" : ""}`}
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        title={`Chat: ${label(ai.chat.model)} · ${ai.chat.effort}\nReviews: ${label(ai.review.model)} · ${ai.review.effort}`}
      >
        <Icon name="sparkle" size={13} /> {label(ai.chat.model)} <span className="model-effort">· {ai.chat.effort}</span>
        <Icon name="chevronDown" size={13} className="skill-chev" />
      </button>

      {open && (
        <div className="model-pop">
          <div className="model-pop-head">
            <strong>Claude settings</strong>
            <span>Pick a model and effort for each use.</span>
          </div>

          <div className="model-section">
            <div className="effort-seg use-seg" role="tablist" aria-label="Use">
              {USES.map((u) => (
                <button key={u.id} role="tab" aria-selected={u.id === use} className={u.id === use ? "on" : ""} onClick={() => setUse(u.id)}>
                  {u.label}
                </button>
              ))}
            </div>
            <p className="model-note">{USES.find((u) => u.id === use)!.desc}</p>
          </div>

          <div className="model-section">
            <div className="model-pop-label">Model</div>
            <div className="model-list" role="radiogroup" aria-label="Model">
              {ai.models.map((m) => {
                const info = MODELS[m.id];
                const on = m.id === current.model;
                return (
                  <button
                    key={m.id}
                    role="radio"
                    aria-checked={on}
                    className={`model-opt ${on ? "on" : ""}`}
                    onClick={() => save({ model: m.id })}
                  >
                    <span className="model-opt-body">
                      <span className="model-opt-name">
                        {m.label}
                        {m.id === ai.defaults[use].model && <span className="model-rec">Default</span>}
                      </span>
                      {info && <span className="model-opt-desc">{info.desc}</span>}
                    </span>
                    {info && <UsageBars level={info.usage} />}
                    <Icon name="check" size={16} className={`skill-check model-check ${on ? "" : "hidden"}`} />
                  </button>
                );
              })}
            </div>
          </div>

          <div className="model-section">
            <div className="model-pop-label">Effort</div>
            <div className="effort-seg" role="radiogroup" aria-label="Effort">
              {ai.efforts.map((e) => (
                <button
                  key={e}
                  role="radio"
                  aria-checked={e === current.effort}
                  className={e === current.effort ? "on" : ""}
                  onClick={() => save({ effort: e })}
                >
                  {e}
                </button>
              ))}
            </div>
            <p className="model-note">{EFFORTS[current.effort]}</p>
            {error && <p className="model-note error">{error}</p>}
          </div>
        </div>
      )}
    </div>
  );
}
