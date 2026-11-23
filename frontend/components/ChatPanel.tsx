"use client";

import { useEffect, useRef, useState } from "react";
import { api, ChatImage, ChatMsg, notifyChat, streamChat } from "@/lib/api";
import { CHAT_MAX, CHAT_MIN, DEFAULT_CHAT_WIDTH, usePref } from "@/lib/prefs";
import Icon from "./Icon";
import Markdown from "./Markdown";

/** Text the learner selected in the lesson, to ask about. `from`/`to` are source lines of the Markdown. */
export type ChatQuote = { text: string; label: string; from?: number; to?: number };
export type ChatDraft = { text: string; quote?: ChatQuote; n: number }; // n changes each time, so the same text can be pushed twice

const quoteTitle = (q: ChatQuote) =>
  q.label + (q.from === undefined ? "" : q.to === undefined || q.to === q.from ? ` · line ${q.from}` : ` · lines ${q.from}–${q.to}`);

/** The quote as a Markdown blockquote, so it renders in the chat and Claude sees the exact lines. */
const quoteMarkdown = (q: ChatQuote) => `> **${quoteTitle(q)}**\n> ${q.text.split("\n").join("\n> ")}\n\n`;

const IMAGE_TYPES = ["image/png", "image/jpeg", "image/gif", "image/webp"];
const MAX_IMAGES = 4;
const MAX_IMAGE_BYTES = 5 * 1024 * 1024;

/** A screenshot waiting to be sent. `url` is a local preview. */
type Attachment = ChatImage & { url: string };

const readBase64 = (file: File) =>
  new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(",")[1] ?? "");
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });

type Props = {
  lessonId: string;
  lessonTitle: string;
  initial: ChatMsg[]; // used once; the parent remounts this panel per lesson
  draft: ChatDraft | null;
  onClose: () => void;
};

const QUICK_PROMPTS = [
  "Explain this lesson in simple words",
  "Give me another example",
  "Quiz me with 3 questions",
  "What do interviewers ask about this?",
];

export default function ChatPanel({ lessonId, lessonTitle, initial, draft, onClose }: Props) {
  const [messages, setMessages] = useState<ChatMsg[]>(initial);
  const [input, setInput] = useState("");
  const [quote, setQuote] = useState<ChatQuote | null>(null);
  const [busy, setBusy] = useState(false);
  const [images, setImages] = useState<Attachment[]>([]);
  const [imageError, setImageError] = useState("");
  const [dragging, setDragging] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);
  const [width, setWidth] = usePref("chatWidth", DEFAULT_CHAT_WIDTH);
  const [expanded, setExpanded] = usePref("chatExpanded", false);
  const logRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const scrollNext = useRef(true); // true on mount (show the latest message of a saved chat)

  useEffect(() => {
    if (draft) {
      if (draft.text) setInput(draft.text);
      if (draft.quote) setQuote(draft.quote);
      inputRef.current?.focus();
    }
  }, [draft]);

  // Scroll to the bottom only when asked (on mount and when the learner sends), never while an
  // answer streams in: the learner is reading above and must not be pulled down.
  useEffect(() => {
    if (!scrollNext.current) return;
    scrollNext.current = false;
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight });
  }, [messages]);

  // Grow the textarea with its content (up to ~8 lines, then scroll).
  useEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  }, [input]);

  useEffect(() => () => abortRef.current?.abort(), []);

  /** Adds pasted, dropped or picked image files as attachments (png, jpeg, gif, webp; up to 4, 5 MB each). */
  const addImages = async (files: File[]) => {
    const pictures = files.filter((f) => f.type.startsWith("image/"));
    if (!pictures.length) return;
    setImageError("");
    const added: Attachment[] = [];
    let error = "";
    for (const file of pictures) {
      if (images.length + added.length >= MAX_IMAGES) error = `At most ${MAX_IMAGES} screenshots per message.`;
      else if (!IMAGE_TYPES.includes(file.type)) error = "Use a PNG, JPEG, GIF or WebP image.";
      else if (file.size > MAX_IMAGE_BYTES) error = "That image is bigger than 5 MB.";
      else added.push({ media_type: file.type, data: await readBase64(file), url: URL.createObjectURL(file) });
    }
    setImageError(error);
    if (added.length) setImages((cur) => [...cur, ...added]);
  };

  const removeImage = (i: number) =>
    setImages((cur) => {
      URL.revokeObjectURL(cur[i].url);
      return cur.filter((_, j) => j !== i);
    });

  const send = async (text?: string) => {
    const typed = (text ?? input).trim();
    if ((!typed && !images.length) || busy) return;
    const question = typed || "Please look at this screenshot and help me.";
    const sent = images;
    const message =
      (quote ? quoteMarkdown(quote) : "") + question + sent.map((im) => `\n\n![screenshot](${im.url})`).join("");
    setInput("");
    setQuote(null);
    setImages([]);
    setImageError("");
    setBusy(true);
    scrollNext.current = true;
    setMessages((m) => [...m, { role: "user", content: message }, { role: "assistant", content: "" }]);
    const setLast = (content: string) => setMessages((m) => [...m.slice(0, -1), { role: "assistant", content }]);
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    let got = "";
    try {
      await streamChat(
        lessonId,
        (quote ? quoteMarkdown(quote) : "") + question,
        (full) => {
          got = full;
          setLast(full);
        },
        ctrl.signal,
        sent.map(({ media_type, data }) => ({ media_type, data })),
      );
    } catch (e) {
      if (ctrl.signal.aborted) setLast((got ? got + "\n\n" : "") + "_Stopped._");
      else setLast(`**Error:** ${(e as Error).message}`);
    } finally {
      abortRef.current = null;
      setBusy(false);
      inputRef.current?.focus();
      notifyChat();
    }
  };

  const clear = async () => {
    if (!confirm("Start a new conversation? This lesson's chat will be cleared.")) return;
    abortRef.current?.abort();
    await api.clearChat(lessonId);
    setMessages([]);
  };

  // Drag the left edge to resize.
  const startResize = (e: React.PointerEvent) => {
    e.preventDefault();
    const startX = e.clientX;
    const startW = width;
    setExpanded(false);
    document.body.classList.add("resizing");
    const move = (ev: PointerEvent) => {
      const w = Math.min(CHAT_MAX, Math.max(CHAT_MIN, startW + (startX - ev.clientX)));
      document.documentElement.style.setProperty("--chat-w", w + "px");
    };
    const up = (ev: PointerEvent) => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
      document.body.classList.remove("resizing");
      document.documentElement.style.removeProperty("--chat-w");
      setWidth(Math.min(CHAT_MAX, Math.max(CHAT_MIN, startW + (startX - ev.clientX))));
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
  };

  const style = { "--chat-w-saved": expanded ? "min(60vw, 1100px)" : `${width}px` } as React.CSSProperties;

  return (
    <aside className="chat" style={style}>
      <div className="chat-resize" onPointerDown={startResize} title="Drag to resize" />

      <div className="chat-head">
        <div className="chat-title">
          <span className="claude-mark">
            <Icon name="sparkle" size={14} />
          </span>
          <div>
            <strong>Claude</strong>
            <div className="chat-sub" title={lessonTitle}>
              Lesson: {lessonTitle}
            </div>
          </div>
        </div>
        <div className="chat-actions">
          <button className="icon-btn small" onClick={clear} title="New conversation">
            <Icon name="plus" size={15} />
          </button>
          <button className="icon-btn small" onClick={() => setExpanded(!expanded)} title={expanded ? "Shrink" : "Expand"}>
            <Icon name={expanded ? "shrink" : "expand"} size={14} />
          </button>
          <button className="icon-btn small" onClick={onClose} title="Hide Claude (⌥⌘B)">
            <Icon name="x" size={15} />
          </button>
        </div>
      </div>

      <div className="chat-log" ref={logRef}>
        {messages.length === 0 ? (
          <div className="chat-empty">
            <span className="claude-mark big">
              <Icon name="sparkle" size={22} />
            </span>
            <h3>Ask me anything about this lesson</h3>
            <p className="muted">I know the lesson content and your exercises. I give hints first, not full answers.</p>
            <div className="chips">
              {QUICK_PROMPTS.map((p) => (
                <button key={p} className="chip" onClick={() => send(p)}>
                  {p}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m, i) =>
            m.role === "user" ? (
              <div key={i} className="msg user">
                <Markdown text={m.content} />
              </div>
            ) : (
              <div key={i} className="msg assistant">
                <div className="msg-label">
                  <span className="claude-mark tiny">
                    <Icon name="sparkle" size={10} />
                  </span>
                  Claude
                </div>
                {m.content ? (
                  <Markdown text={m.content} />
                ) : (
                  <div className="typing">
                    <span />
                    <span />
                    <span />
                  </div>
                )}
              </div>
            ),
          )
        )}
      </div>

      <form
        className={`chat-form ${dragging ? "dragging" : ""}`}
        onSubmit={(e) => {
          e.preventDefault();
          send();
        }}
        onDragOver={(e) => {
          if (e.dataTransfer.types.includes("Files")) {
            e.preventDefault();
            setDragging(true);
          }
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          addImages(Array.from(e.dataTransfer.files));
        }}
      >
        {quote && (
          <div className="chat-quote">
            <div className="chat-quote-head">
              <strong>{quoteTitle(quote)}</strong>
              <button type="button" className="icon-btn small" onClick={() => setQuote(null)} title="Remove the selection">
                <Icon name="x" size={13} />
              </button>
            </div>
            <div className="chat-quote-text">{quote.text}</div>
          </div>
        )}
        {images.length > 0 && (
          <div className="chat-attachments">
            {images.map((im, i) => (
              <div key={im.url} className="chat-thumb">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={im.url} alt={`Screenshot ${i + 1}`} />
                <button type="button" className="chat-thumb-x" onClick={() => removeImage(i)} title="Remove screenshot">
                  <Icon name="x" size={11} />
                </button>
              </div>
            ))}
          </div>
        )}
        {imageError && <div className="chat-image-error">{imageError}</div>}
        <div className="chat-input-box">
          <input
            ref={fileInput}
            type="file"
            accept={IMAGE_TYPES.join(",")}
            multiple
            hidden
            onChange={(e) => {
              addImages(Array.from(e.target.files ?? []));
              e.target.value = "";
            }}
          />
          <button
            type="button"
            className="icon-btn small attach-btn"
            onClick={() => fileInput.current?.click()}
            disabled={busy || images.length >= MAX_IMAGES}
            title="Attach a screenshot (or paste / drop one)"
          >
            <Icon name="plus" size={15} />
          </button>
          <textarea
            id="chat-input"
            ref={inputRef}
            rows={1}
            value={input}
            placeholder={quote ? "Ask about this selection…" : images.length ? "Ask about the screenshot…" : "Ask Claude…"}
            onChange={(e) => setInput(e.target.value)}
            onPaste={(e) => {
              const files = Array.from(e.clipboardData.files).filter((f) => f.type.startsWith("image/"));
              if (files.length) {
                e.preventDefault();
                addImages(files);
              }
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
          />
          {busy ? (
            <button type="button" className="send-btn stop" onClick={() => abortRef.current?.abort()} title="Stop">
              <Icon name="stop" size={14} />
            </button>
          ) : (
            <button className="send-btn" disabled={!input.trim() && !images.length} title="Send">
              <Icon name="send" size={15} />
            </button>
          )}
        </div>
        <div className="chat-hint">Enter to send · Shift+Enter for a new line · paste or drop a screenshot · / to focus</div>
      </form>
    </aside>
  );
}
