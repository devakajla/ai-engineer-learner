"use client";

import { useEffect } from "react";
import { applyTheme, ThemePref, usePref } from "@/lib/prefs";
import Icon from "./Icon";

const NEXT: Record<ThemePref, ThemePref> = { system: "light", light: "dark", dark: "system" };
const ICON = { system: "monitor", light: "sun", dark: "moon" } as const;

export default function ThemeToggle() {
  const [theme, setTheme] = usePref<ThemePref>("theme", "system");

  useEffect(() => {
    applyTheme(theme);
    if (theme !== "system") return;
    const mq = matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => applyTheme("system");
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, [theme]);

  return (
    <button className="icon-btn" onClick={() => setTheme(NEXT[theme])} title={`Theme: ${theme} (click to change)`}>
      <Icon name={ICON[theme]} />
    </button>
  );
}
