"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import ChatPanel, { ChatDraft } from "@/components/ChatPanel";
import { DoubtDialog, DoubtList, DoubtSpot } from "@/components/Doubts";
import Icon from "@/components/Icon";
import Markdown, { Heading } from "@/components/Markdown";
import { NotesDialog } from "@/components/Notes";
import Practice from "@/components/Practice";
import Project from "@/components/Project";
import Quiz from "@/components/Quiz";
import Sidebar from "@/components/Sidebar";
import { api, CHAT_EVENT, Doubt, DOUBTS_EVENT, Lesson, notifyProgress, TrackDetail } from "@/lib/api";
import { usePref } from "@/lib/prefs";
import { useTextSelection } from "@/lib/useTextSelection";
import VideoSegment from "@/components/VideoSegment";

type Tab = "theory" | "quiz" | "practice" | "project";

const STATUS_LABEL = { not_started: "Not started", learning: "In progress", done: "Completed" } as const;
const TAB_LABEL: Record<Tab, string> = { theory: "Theory", quiz: "Quiz", practice: "Practice", project: "Project" };

export default function LessonPage() {
  const { track: trackId, slug } = useParams<{ track: string; slug: string }>();
  const router = useRouter();
  const [track, setTrack] = useState<TrackDetail | null>(null);
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [tab, setTab] = useState<Tab>("theory");
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = usePref("sidebarOpen", true);
  const [chatOpen, setChatOpen] = usePref("chatOpen", true);
  const [chatDraft, setChatDraft] = useState<ChatDraft | null>(null);
  const [readPct, setReadPct] = useState(0);
  const [doubtSpot, setDoubtSpot] = useState<DoubtSpot | null>(null);
  const [activeExercise, setActiveExercise] = useState("");
  const [notesDialog, setNotesDialog] = useState<null | { generate: boolean }>(null);
  const contentRef = useRef<HTMLElement>(null);
  const selection = useTextSelection(contentRef);
  const cmdL = useRef<() => void>(() => {}); // latest "Cmd+L" action; set below, after the early returns

  // Cmd/Ctrl+L: quote the selected text in the chat, or just focus the chat when nothing is selected.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && !e.shiftKey && !e.altKey && e.code === "KeyL") {
        e.preventDefault(); // the browser would focus the address bar
        cmdL.current();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    let stale = false; // ignore results from an outdated run (fast navigation, React dev double-run)
    setError("");
    // The plan's Start button opens the first step that is not done: /track/slug?tab=quiz
    const want = new URLSearchParams(window.location.search).get("tab");
    setTab(want === "quiz" || want === "practice" || want === "project" ? want : "theory");
    // Loading the lesson marks it "learning", so refresh the sidebar after it.
    api
      .lesson(trackId, slug)
      .then((l) => {
        if (stale) return;
        setLesson(l);
        return api.track(trackId).then((t) => {
          if (stale) return;
          setTrack(t);
          notifyProgress();
        });
      })
      .catch((e) => !stale && setError(e.message));
    return () => {
      stale = true;
    };
  }, [trackId, slug]);

  // Coming from the revise list (/track/slug#heading): scroll to the starred spot once the lesson is shown.
  const loadedId = lesson?.slug === slug ? lesson.id : null;
  useEffect(() => {
    const hash = decodeURIComponent(window.location.hash.slice(1));
    if (loadedId && hash) setTimeout(() => document.getElementById(hash)?.scrollIntoView({ block: "start" }), 50);
  }, [loadedId]);

  // Doubt stars in the sidebar follow changes made anywhere.
  useEffect(() => {
    const reload = () =>
      api
        .track(trackId)
        .then(setTrack)
        .catch(() => {});
    window.addEventListener(DOUBTS_EVENT, reload);
    return () => window.removeEventListener(DOUBTS_EVENT, reload);
  }, [trackId]);

  // The "new chat" dot on the notes button follows the chat.
  useEffect(() => {
    const reload = () =>
      api
        .note(`${trackId}/${slug}`)
        .then((note) => setLesson((l) => (l && l.id === `${trackId}/${slug}` ? { ...l, note } : l)))
        .catch(() => {});
    window.addEventListener(CHAT_EVENT, reload);
    return () => window.removeEventListener(CHAT_EVENT, reload);
  }, [trackId, slug]);

  // On small screens the sidebar is a drawer: close it after navigating.
  useEffect(() => {
    if (window.innerWidth < 900) setSidebarOpen(false);
  }, [slug, setSidebarOpen]);

  const switchTab = (t: Tab) => {
    setTab(t);
    contentRef.current?.scrollTo({ top: 0 });
  };

  const onScroll = () => {
    const el = contentRef.current;
    if (!el) return;
    const max = el.scrollHeight - el.clientHeight;
    setReadPct(max > 0 ? Math.min(100, (100 * el.scrollTop) / max) : 0);
  };

  const setDone = async (done: boolean) => {
    if (!lesson) return;
    const { status } = await api.setProgress(lesson.id, done ? "done" : "learning");
    setLesson({ ...lesson, status });
    setTrack(await api.track(trackId));
    notifyProgress();
  };

  const finishAndNext = async () => {
    await setDone(true);
    if (lesson?.next?.available) router.push(`/${trackId}/${lesson.next.slug}`);
  };

  const doubts = lesson?.doubts;
  const setDoubts = (list: Doubt[]) => setLesson((l) => l && { ...l, doubts: list });
  const starred = useMemo(
    () => new Set((doubts ?? []).filter((d) => !d.resolved && d.anchor).map((d) => d.anchor as string)),
    [doubts],
  );
  const closeDoubt = useCallback(() => setDoubtSpot(null), []);
  const starHeading = useCallback((h: Heading) => setDoubtSpot({ location: `Theory › ${h.text}`, anchor: h.id }), []);

  /** "Mark doubt" button: the spot is the current tab (and exercise), editable in the dialog. */
  const markDoubt = () => {
    const where = TAB_LABEL[tab] + (tab === "practice" && activeExercise ? ` › ${activeExercise}` : "");
    setDoubtSpot({ location: where, anchor: null });
  };

  const goToDoubt = (d: Doubt) => {
    const tabName = (Object.keys(TAB_LABEL) as Tab[]).find((t) => d.location.startsWith(TAB_LABEL[t]));
    if (tabName && tabName !== tab) switchTab(tabName);
    if (d.anchor)
      setTimeout(() => document.getElementById(d.anchor!)?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
  };

  if (error) return <div className="center-msg error">{error}</div>;
  if (!lesson || !track || lesson.slug !== slug) return <div className="center-msg">Loading…</div>;

  // Where this lesson sits: level name and position in the track.
  const all = track.levels.flatMap((lv) => lv.lessons.map((l) => ({ l, level: lv.title.split("—")[0].trim() })));
  const position = all.findIndex((x) => x.l.id === lesson.id);
  const levelName = all[position]?.level ?? "";
  const minutes = Math.max(1, Math.round(lesson.body.split(/\s+/).length / 200));

  const solvedCount = lesson.exercises.filter((e) => e.solved).length;
  const steps: { id: Tab; label: string; done: boolean; extra?: string; disabled: boolean }[] = [
    { id: "theory", label: "Theory", done: lesson.status === "done" || !!lesson.last_quiz, disabled: false },
    {
      id: "quiz",
      label: "Quiz",
      done: !!lesson.last_quiz,
      extra: lesson.last_quiz ? `${lesson.last_quiz.score}/${lesson.last_quiz.total}` : `${lesson.quiz.length} Qs`,
      disabled: !lesson.quiz.length,
    },
    {
      id: "practice",
      label: "Practice",
      done: lesson.exercises.length > 0 && solvedCount === lesson.exercises.length,
      extra: `${solvedCount}/${lesson.exercises.length}`,
      disabled: !lesson.exercises.length,
    },
  ];
  if (lesson.project) {
    steps.push({
      id: "project",
      label: "Project",
      done: lesson.project.passed,
      extra: lesson.project.passed ? "passed" : lesson.project.name,
      disabled: false,
    });
  }
  const practiceDone = steps[2].done;
  const allDone = practiceDone && (!lesson.project || lesson.project.passed);

  const askClaude = (text: string) => {
    setChatOpen(true);
    setChatDraft((d) => ({ text, n: (d?.n ?? 0) + 1 }));
  };

  /** "Ask Claude" on selected text: attach it (with its tab and lines) to the chat as a quote. */
  const quoteToChat = () => {
    if (!selection) return;
    const label = TAB_LABEL[tab] + (tab === "practice" && activeExercise ? ` › ${activeExercise}` : "");
    const hasLines = tab !== "quiz" && selection.from !== undefined; // quiz Markdown restarts at line 1 per question
    setChatOpen(true);
    setChatDraft((d) => ({
      text: "",
      quote: { text: selection.text, label, from: hasLines ? selection.from : undefined, to: hasLines ? selection.to : undefined },
      n: (d?.n ?? 0) + 1,
    }));
    window.getSelection()?.removeAllRanges();
  };

  cmdL.current = () => {
    // Same quote card as the "Ask Claude" button. Read the live selection too: the `selection`
    // state is only refreshed after mouse/key release, so it can lag behind.
    if (selection) return quoteToChat();
    const live = window.getSelection();
    const text = live && !live.isCollapsed && contentRef.current?.contains(live.anchorNode) ? live.toString().trim() : "";
    if (text) {
      setChatOpen(true);
      setChatDraft((d) => ({
        text: "",
        quote: { text: text.length > 2000 ? text.slice(0, 2000) + "…" : text, label: TAB_LABEL[tab] },
        n: (d?.n ?? 0) + 1,
      }));
      live?.removeAllRanges();
      return;
    }
    setChatOpen(true);
    setTimeout(() => document.getElementById("chat-input")?.focus(), 50);
  };

  return (
    <div className={`layout ${sidebarOpen ? "" : "sidebar-hidden"} ${chatOpen ? "" : "chat-hidden"}`}>
      {sidebarOpen && (
        <>
          <Sidebar track={track} currentId={lesson.id} onClose={() => setSidebarOpen(false)} />
          <div className="drawer-backdrop" onClick={() => setSidebarOpen(false)} />
        </>
      )}

      <main className="content" ref={contentRef} onScroll={onScroll}>
        <div className="read-progress" style={{ width: `${readPct}%` }} />
        <div className="content-inner">
          <div className="crumbs">
            <span>{track.title}</span>
            <Icon name="chevronRight" size={12} />
            <span>{levelName}</span>
            <Icon name="chevronRight" size={12} />
            <span>
              Lesson {position + 1} of {all.length}
            </span>
          </div>

          <h1>{lesson.title}</h1>
          {lesson.summary && <p className="summary">{lesson.summary}</p>}

          <div className="meta-row">
            <span className={`pill ${lesson.status === "done" ? "good" : "neutral"}`}>
              {STATUS_LABEL[lesson.status]}
            </span>
            {lesson.kind === "interview" && <span className="pill warn">Interview module</span>}
            <span className="meta">
              <Icon name="clock" size={13} /> {minutes} min read
            </span>
            {lesson.plan_ids.map((p) => (
              <span key={p} className="tag">
                {p}
              </span>
            ))}
            <button
              className="btn ghost small doubt-btn push-right"
              onClick={markDoubt}
              title="Star this spot as doubtful, with a note"
            >
              <Icon name="star" size={14} /> Mark doubt
            </button>
          </div>

          <DoubtList doubts={lesson.doubts} onChange={setDoubts} onGo={goToDoubt} />

          <div className="stepper" role="tablist">
            {steps.map((s, i) => (
              <button
                key={s.id}
                role="tab"
                aria-selected={tab === s.id}
                className={`step ${tab === s.id ? "active" : ""} ${s.done ? "done" : ""}`}
                disabled={s.disabled}
                onClick={() => switchTab(s.id)}
              >
                <span className="step-num">{s.done ? <Icon name="check" size={12} /> : i + 1}</span>
                <span className="step-label">{s.label}</span>
                {s.extra && <span className="step-extra">{s.extra}</span>}
              </button>
            ))}
          </div>

          {/* Panels stay mounted so quiz answers and editor code survive tab switches. */}
          <section hidden={tab !== "theory"} className="prose">
            {lesson.intro_video && <VideoSegment video={lesson.intro_video} label="Intro video" />}
            <Markdown text={lesson.body} onStar={starHeading} starred={starred} />
            {lesson.quiz.length > 0 ? (
              <div className="cta-card">
                <div>
                  <strong>Check your understanding</strong>
                  <span className="muted">{lesson.quiz.length} quick questions on this lesson.</span>
                </div>
                <button className="btn primary" onClick={() => switchTab("quiz")}>
                  Take the quiz <Icon name="arrowRight" size={14} />
                </button>
              </div>
            ) : (
              lesson.exercises.length > 0 && (
                <div className="cta-card">
                  <div>
                    <strong>Time to practise</strong>
                    <span className="muted">{lesson.exercises.length} exercises.</span>
                  </div>
                  <button className="btn primary" onClick={() => switchTab("practice")}>
                    Start practice <Icon name="arrowRight" size={14} />
                  </button>
                </div>
              )
            )}
          </section>
          {lesson.quiz.length > 0 && (
            <section hidden={tab !== "quiz"}>
              <Quiz
                key={lesson.id}
                lesson={lesson}
                onScored={(score, total) => setLesson((l) => l && { ...l, last_quiz: { score, total } })}
                onNext={lesson.exercises.length ? () => switchTab("practice") : undefined}
              />
            </section>
          )}
          {lesson.exercises.length > 0 && (
            <section hidden={tab !== "practice"}>
              <Practice
                key={lesson.id}
                lesson={lesson}
                onSolved={(id) =>
                  setLesson(
                    (l) => l && { ...l, exercises: l.exercises.map((e) => (e.id === id ? { ...e, solved: true } : e)) },
                  )
                }
                onAskClaude={askClaude}
                onActive={(e) => setActiveExercise(e.title)}
              />
              {practiceDone && lesson.project && !lesson.project.passed && (
                <div className="cta-card">
                  <div>
                    <strong>Exercises done — now build it for real</strong>
                    <span className="muted">Apply this lesson to your {lesson.project.name} project.</span>
                  </div>
                  <button className="btn primary" onClick={() => switchTab("project")}>
                    Go to project step <Icon name="arrowRight" size={14} />
                  </button>
                </div>
              )}
              {allDone && lesson.status !== "done" && (
                <div className="cta-card good">
                  <div>
                    <strong>All exercises solved 🎉</strong>
                    <span className="muted">Mark this lesson as done and continue.</span>
                  </div>
                  <button className="btn primary" onClick={finishAndNext}>
                    Mark done & next <Icon name="arrowRight" size={14} />
                  </button>
                </div>
              )}
            </section>
          )}

          {lesson.project && (
            <section hidden={tab !== "project"}>
              <Project
                key={lesson.id}
                lesson={lesson}
                onPassed={() => setLesson((l) => l && l.project && { ...l, project: { ...l.project, passed: true } })}
                onAskClaude={askClaude}
              />
              {allDone && lesson.status !== "done" && (
                <div className="cta-card good">
                  <div>
                    <strong>Lesson complete 🎉</strong>
                    <span className="muted">Exercises solved and project checkpoint passed.</span>
                  </div>
                  <button className="btn primary" onClick={finishAndNext}>
                    Mark done & next <Icon name="arrowRight" size={14} />
                  </button>
                </div>
              )}
            </section>
          )}

          <div className="lesson-footer">
            <div className="done-row">
              {lesson.status === "done" ? (
                <button className="btn done" onClick={() => setDone(false)} title="Click to mark as not done">
                  <Icon name="check" size={14} /> Completed
                </button>
              ) : (
                <button className="btn primary" onClick={() => setDone(true)}>
                  Mark lesson as done
                </button>
              )}
              <button
                className="btn"
                onClick={() => setNotesDialog({ generate: !lesson.note.exists || lesson.note.has_new_chat })}
                title={lesson.note.exists ? "Add what you asked since the last save" : "Write revision notes for this lesson"}
              >
                <Icon name="book" size={14} />
                {lesson.note.exists ? (lesson.note.has_new_chat ? "Update notes" : "View notes") : "Make notes"}
                {lesson.note.has_new_chat && lesson.note.exists && <span className="notes-dot" aria-label="New chat to add" />}
              </button>
            </div>
            <nav className="pager">
              {lesson.prev ? (
                <Link className="pager-card" href={`/${trackId}/${lesson.prev.slug}`}>
                  <span className="pager-dir">
                    <Icon name="arrowLeft" size={13} /> Previous
                  </span>
                  <span className="pager-title">{lesson.prev.title}</span>
                </Link>
              ) : (
                <span />
              )}
              {lesson.next ? (
                lesson.next.available ? (
                  <Link className="pager-card next" href={`/${trackId}/${lesson.next.slug}`}>
                    <span className="pager-dir">
                      Next <Icon name="arrowRight" size={13} />
                    </span>
                    <span className="pager-title">{lesson.next.title}</span>
                  </Link>
                ) : (
                  <span className="pager-card next disabled">
                    <span className="pager-dir">Next · coming soon</span>
                    <span className="pager-title">{lesson.next.title}</span>
                  </span>
                )
              ) : (
                <span />
              )}
            </nav>
          </div>
        </div>
      </main>

      {selection && (
        <button
          className="ask-selection"
          style={{
            top: selection.rect.top > 52 ? selection.rect.top - 42 : selection.rect.bottom + 8,
            left: Math.min(Math.max(8, selection.rect.left + selection.rect.width / 2 - 55), window.innerWidth - 124),
          }}
          onMouseDown={(e) => e.preventDefault()} // keep the selection until we have read it
          onClick={quoteToChat}
        >
          <Icon name="sparkle" size={13} /> Ask Claude
        </button>
      )}

      {doubtSpot && (
        <DoubtDialog
          key={doubtSpot.location}
          lessonId={lesson.id}
          spot={doubtSpot}
          onSaved={(d) => setLesson((l) => l && { ...l, doubts: [...l.doubts, d] })}
          onClose={closeDoubt}
        />
      )}

      {notesDialog && (
        <NotesDialog
          key={`notes-${lesson.id}`}
          lessonId={lesson.id}
          lessonTitle={lesson.title}
          note={lesson.note}
          generate={notesDialog.generate}
          onSaved={(note) => setLesson((l) => l && { ...l, note })}
          onClose={() => setNotesDialog(null)}
        />
      )}

      {chatOpen && (
        <ChatPanel
          key={lesson.id}
          lessonId={lesson.id}
          lessonTitle={lesson.title}
          initial={lesson.chat}
          draft={chatDraft}
          onClose={() => setChatOpen(false)}
        />
      )}
    </div>
  );
}
