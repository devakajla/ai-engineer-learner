"use client";

// Small UI preferences kept in localStorage and shared between components
// (e.g. the top bar toggles the sidebar that the lesson page renders).

import { useCallback, useEffect, useState } from "react";

const EVENT = "learner:pref";

export type ThemePref = "system" | "light" | "dark";

export const DEFAULT_CHAT_WIDTH = 440;
export const CHAT_MIN = 320;
export const CHAT_MAX = 900;

function read<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem("learner." + key);
    return raw === null ? fallback : (JSON.parse(raw) as T);
  } catch {
    return fallback;
  }
}

export function writePref<T>(key: string, value: T) {
  try {
    localStorage.setItem("learner." + key, JSON.stringify(value));
  } catch {}
  window.dispatchEvent(new CustomEvent(EVENT, { detail: { key, value } }));
}

/** Like useState, but persisted and synced across components. Starts at `fallback` on the server. */
export function usePref<T>(key: string, fallback: T): [T, (v: T | ((prev: T) => T)) => void] {
  const [value, setValue] = useState<T>(fallback);

  useEffect(() => {
    setValue(read(key, fallback));
    const onPref = (e: Event) => {
      const { key: k, value: v } = (e as CustomEvent).detail;
      if (k === key) setValue(v);
    };
    window.addEventListener(EVENT, onPref);
    return () => window.removeEventListener(EVENT, onPref);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  const set = useCallback(
    (v: T | ((prev: T) => T)) => {
      const next = typeof v === "function" ? (v as (p: T) => T)(read(key, fallback)) : v;
      writePref(key, next);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [key],
  );

  return [value, set];
}

export function applyTheme(pref: ThemePref) {
  const dark = pref === "dark" || (pref === "system" && matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.dataset.theme = dark ? "dark" : "light";
}

/** The theme actually shown ("light" | "dark"), following the <html data-theme> attribute. */
export function useResolvedTheme(): "light" | "dark" {
  const [theme, setTheme] = useState<"light" | "dark">("light");
  useEffect(() => {
    const el = document.documentElement;
    const update = () => setTheme(el.dataset.theme === "dark" ? "dark" : "light");
    update();
    const obs = new MutationObserver(update);
    obs.observe(el, { attributes: true, attributeFilter: ["data-theme"] });
    return () => obs.disconnect();
  }, []);
  return theme;
}

/** Runs before first paint (inlined in <head>) so the page never flashes the wrong theme. */
export const THEME_BOOT_SCRIPT = `(function(){try{var p=JSON.parse(localStorage.getItem("learner.theme")||'"system"');var d=p==="dark"||(p==="system"&&matchMedia("(prefers-color-scheme: dark)").matches);document.documentElement.dataset.theme=d?"dark":"light";}catch(e){document.documentElement.dataset.theme="light";}})();`;

/** True when a keyboard shortcut should be ignored because the user is typing. */
export function isTyping(e: KeyboardEvent) {
  const t = e.target as HTMLElement | null;
  return !!t && (t.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(t.tagName) || !!t.closest(".cm-editor"));
}
