import { RefObject, useEffect, useState } from "react";

export type TextSelection = {
  text: string;
  /** Source lines of the selection (from the Markdown), when known. */
  from?: number;
  to?: number;
  /** Where to show the "Ask Claude" button (viewport coordinates). */
  rect: { top: number; bottom: number; left: number; width: number };
};

const MAX_CHARS = 2000;
// Selections inside these are about code being typed, not text being read.
const IGNORE = "textarea, input, .cm-editor, .monaco-editor, [data-no-ask]";

const elementOf = (n: Node | null) => (n instanceof Element ? n : (n?.parentElement ?? null));

/** The text the learner has selected inside `ref`, with the source line range of the Markdown it came from. */
export function useTextSelection(ref: RefObject<HTMLElement | null>): TextSelection | null {
  const [sel, setSel] = useState<TextSelection | null>(null);

  useEffect(() => {
    const read = () => {
      const s = window.getSelection();
      const root = ref.current;
      if (!s || !root || s.isCollapsed || s.rangeCount === 0) return setSel(null);
      const range = s.getRangeAt(0);
      const start = elementOf(range.startContainer);
      const end = elementOf(range.endContainer);
      if (!start || !end || !root.contains(start) || !root.contains(end)) return setSel(null);
      if (start.closest(IGNORE) || end.closest(IGNORE)) return setSel(null);
      const text = s.toString().trim();
      if (!text) return setSel(null);

      const l1 = start.closest("[data-l1]");
      const l2 = end.closest("[data-l2]");
      const from = l1 ? Number(l1.getAttribute("data-l1")) : undefined;
      const to = l2 ? Number(l2.getAttribute("data-l2")) : undefined;
      const r = range.getBoundingClientRect();
      setSel({
        text: text.length > MAX_CHARS ? text.slice(0, MAX_CHARS) + "…" : text,
        from: from !== undefined && to !== undefined ? Math.min(from, to) : from,
        to: from !== undefined && to !== undefined ? Math.max(from, to) : to,
        rect: { top: r.top, bottom: r.bottom, left: r.left, width: r.width },
      });
    };
    // Wait a tick after mouseup so the browser has finished updating the selection.
    const onUp = () => setTimeout(read, 0);
    const onChange = () => {
      if (window.getSelection()?.isCollapsed) setSel(null);
    };
    document.addEventListener("mouseup", onUp);
    document.addEventListener("keyup", onUp);
    document.addEventListener("selectionchange", onChange);
    return () => {
      document.removeEventListener("mouseup", onUp);
      document.removeEventListener("keyup", onUp);
      document.removeEventListener("selectionchange", onChange);
    };
  }, [ref]);

  return sel;
}
