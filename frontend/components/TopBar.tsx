"use client";

import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { api, PROGRESS_EVENT, TrackSummary } from "@/lib/api";
import { isTyping, usePref } from "@/lib/prefs";
import { ReviseMenu } from "./Doubts";
import Icon from "./Icon";
import Logo from "./Logo";
import ModelMenu from "./ModelMenu";
import SkillMenu from "./SkillMenu";
import ThemeToggle from "./ThemeToggle";

export default function TopBar() {
  const params = useParams<{ track?: string; slug?: string }>();
  const [tracks, setTracks] = useState<TrackSummary[]>([]);
  const [offline, setOffline] = useState(false);
  const [sidebarOpen, setSidebarOpen] = usePref("sidebarOpen", true);
  const [chatOpen, setChatOpen] = usePref("chatOpen", true);
  const inLesson = !!params.slug;
  const inNotes = usePathname().startsWith("/notes/");

  useEffect(() => {
    const load = () =>
      api
        .tracks()
        .then((t) => {
          setTracks(t);
          setOffline(false);
        })
        .catch(() => setOffline(true));
    load();
    window.addEventListener(PROGRESS_EVENT, load);
    return () => window.removeEventListener(PROGRESS_EVENT, load);
  }, []);

  // Cmd/Ctrl+B or [ toggles the sidebar, Cmd/Ctrl+Option+B or ] toggles chat, / focuses the chat input.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      // Cmd shortcuts work everywhere, even while typing (like VS Code).
      // e.code, not e.key: on macOS Option+B types "∫", so e.key is not "b".
      if ((e.metaKey || e.ctrlKey) && !e.shiftKey && e.code === "KeyB") {
        e.preventDefault();
        if (e.altKey) setChatOpen((o) => !o);
        else setSidebarOpen((o) => !o);
        return;
      }
      if (isTyping(e) || e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.key === "[") setSidebarOpen((o) => !o);
      else if (e.key === "]") setChatOpen((o) => !o);
      else if (e.key === "/") {
        e.preventDefault();
        setChatOpen(true);
        setTimeout(() => document.getElementById("chat-input")?.focus(), 50);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [setSidebarOpen, setChatOpen]);

  return (
    <header className="topbar">
      {inLesson && (
        <button
          className={`icon-btn ${sidebarOpen ? "on" : ""}`}
          onClick={() => setSidebarOpen(!sidebarOpen)}
          title="Toggle lessons panel (⌘B)"
        >
          <Icon name="sidebar" />
        </button>
      )}
      <Link href="/" className="brand" aria-label="Learner home">
        <Logo />
      </Link>
      <span className="topbar-sep" />
      <SkillMenu tracks={tracks} current={params.track} />
      <div className="spacer" />
      {offline && <span className="offline">Backend not running on :8000</span>}
      {!offline && params.track && (
        <Link
          href={inNotes ? `/${params.track}` : `/notes/${params.track}`}
          className={`btn small ${inNotes ? "soft" : "ghost model-btn"}`}
          title={inNotes ? "Back to the lessons" : "Revision notes by module"}
        >
          {inNotes ? (
            <>
              <Icon name="arrowLeft" size={14} /> Back to lessons
            </>
          ) : (
            <>
              <Icon name="book" size={14} /> Notes
            </>
          )}
        </Link>
      )}
      {!offline && <ReviseMenu />}
      {!offline && <ModelMenu />}
      <ThemeToggle />
      {inLesson && (
        <button
          className={`btn small ${chatOpen ? "soft" : ""}`}
          onClick={() => setChatOpen(!chatOpen)}
          title="Toggle Claude panel (⌥⌘B)"
        >
          <Icon name="sparkle" size={14} /> Ask Claude
        </button>
      )}
    </header>
  );
}
