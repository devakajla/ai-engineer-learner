// Talks to the FastAPI backend. All types mirror app/routers/*.py.

export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Status = "not_started" | "learning" | "done";

export type LessonRef = {
  id: string; // "<track>/<slug>"
  slug: string;
  title: string;
  kind: "lesson" | "interview";
  available: boolean;
  status: Status;
  doubts: number; // open doubts in this lesson (only filled in track detail)
};

export type TrackSummary = {
  id: string;
  title: string;
  done: number;
  total: number;
  percent: number;
  next_up: LessonRef | null;
};

export type TrackDetail = TrackSummary & {
  levels: { id: string; title: string; lessons: LessonRef[] }[];
};

export type QuizQuestion = { q: string; type: "single" | "multi"; options: string[] };

export type Video = { video_id: string; title: string; start: number; end: number | null };

export type Exercise = {
  id: string;
  title: string;
  prompt: string;
  starter: string;
  latest_code: string | null;
  solved: boolean;
  video: Video | null;
  tools: { name: string; lesson_id: string | null }[]; // Python tools the exercise needs (no code)
  help: ExerciseHelpState;
};

/** Help used on one exercise. The walkthrough opens after 3 failed runs and Coach hint level 3. */
export type ExerciseHelpState = { coach_level: number; walkthrough: boolean; fails: number; walkthrough_ready: boolean };

export type ProjectStep = {
  name: string; // "TaskFlow" or "DevDocs Copilot", depends on the track
  title: string;
  instructions: string;
  has_check: boolean;
  passed: boolean;
  project_dir: string;
};

export type CheckResult = {
  check_id: number;
  passed: boolean;
  summary: string;
  output: string;
  seconds: number;
  project_dir: string;
  failures?: Failure[];
};

export type Doubt = {
  id: number;
  lesson_id: string;
  lesson_title: string;
  track: string;
  slug: string;
  location: string; // where the doubt came up, e.g. "Theory › Strings"
  anchor: string | null; // heading id to scroll back to
  note: string;
  resolved: boolean;
  created_at: string | null;
};

export type NoteState = {
  exists: boolean;
  body: string;
  updated_at: string | null;
  latest_chat_id: number; // last chat message id, to tell the server what a saved note covers
  has_new_chat: boolean; // chat happened after the note was last saved
};

export type TrackNotes = {
  id: string;
  title: string;
  levels: {
    id: string;
    title: string;
    lessons: {
      id: string;
      slug: string;
      title: string;
      available: boolean;
      note: { body: string; updated_at: string | null } | null;
    }[];
  }[];
};

export type ChatMsg = { role: "user" | "assistant"; content: string };

export type Lesson = {
  id: string;
  track: string;
  slug: string;
  title: string;
  summary: string;
  plan_ids: string[];
  kind: "lesson" | "interview";
  status: Status;
  body: string;
  quiz: QuizQuestion[];
  last_quiz: { score: number; total: number } | null;
  intro_video: Video | null;
  exercises: Exercise[];
  project: ProjectStep | null;
  chat: ChatMsg[];
  doubts: Doubt[];
  note: NoteState;
  prev: LessonRef | null;
  next: LessonRef | null;
};

export type QuizResult = {
  score: number;
  total: number;
  results: { correct: boolean; answer: number[]; explain: string }[];
};

export type Failure = {
  test: string;
  kind: "assertion" | "exception" | "syntax" | "import";
  exc_type: string;
  message: string;
  got: string | null;
  expected: string | null;
  line: number | null;
  source: string;
  hint: string;
};

export type RunResult = {
  submission_id: number;
  passed: boolean;
  summary: string;
  output: string;
  seconds: number;
  failures: Failure[];
};

export type AIUse = "chat" | "review";
export type AIChoice = { model: string; effort: string };
export type AISettings = {
  chat: AIChoice;
  review: AIChoice;
  defaults: Record<AIUse, AIChoice>;
  models: { id: string; label: string }[];
  efforts: string[];
};

export type Gate = {
  quiz?: { best: number | null; need: number; ok: boolean };
  exercises?: { solved: number; total: number; ok: boolean };
  bonus?: { solved: number; total: number }; // optional exercises, never needed for done
  project?: { ok: boolean };
};

export type RoadmapTask = {
  id: string;
  date: string; // YYYY-MM-DD
  kind: "practise" | "review";
  title: string;
  minutes: number;
  steps: string[]; // what to do, in order
  part?: [number, number]; // [this day, total days] for work that spans several days
  track?: string;
  track_label?: string; // "Python", "FastAPI", "Agentic AI", ...
  lesson?: string; // site lesson = /<track>/<lesson>
  available?: boolean; // false = lesson is not written yet
  planned?: boolean;
  ready_by?: string;
  links?: { track: string; lesson: string; title: string }[];
  gated: boolean; // true: done by passing the quiz and exercises, false: tick by hand
  gate: Gate | null;
  tab?: "theory" | "quiz" | "practice" | "project"; // where Start opens the lesson
  done: boolean;
};

export type RoadmapDay = { date: string; tasks: RoadmapTask[] };

export type Roadmap = {
  title: string;
  today: string;
  start: string | null;
  end: string | null;
  state: "empty" | "before" | "running" | "after";
  day_number: number;
  total_days: number;
  tasks: RoadmapTask[];
  overdue: RoadmapTask[];
  streak: number;
  best_streak: number;
  due_count: number;
  done_count: number;
  labels: Record<string, string>;
  days: RoadmapDay[];
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(API + path, { cache: "no-store", ...init });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {}
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return res.json();
}

const json = (body: unknown): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export type ScriptResult = { stdout: string; stderr: string; seconds: number; timed_out: boolean };

/** One weak topic = one Python lesson (see app/services/profile.py). */
export type WeakTopic = {
  tag: string; // lesson slug, e.g. "11-dicts", or "other"
  title: string;
  score: number;
  coach: number;
  chat: number;
  failed: { exercise: string; fails: number; solved: boolean }[];
  drills_done: number;
  drills_total: number;
  details: string[];
  last: string | null;
};
export type TrialDrill = {
  id: number;
  tag: string;
  title: string;
  prompt: string;
  starter: string;
  calls: string[];
  status: "open" | "done";
};
export type DrillCheck = {
  passed: boolean;
  results: { call: string; ok: boolean; got: string; want: string | null }[];
  error: string;
  status: "open" | "done";
};

export const api = {
  trialRun: (code: string) => {
    const form = new FormData();
    form.append("code", code);
    return request<ScriptResult>("/api/trial/run", { method: "POST", body: form });
  },
  trialTopics: () => request<WeakTopic[]>("/api/trial/topics"),
  trialDrills: (tag: string) => request<TrialDrill[]>(`/api/trial/drills?tag=${encodeURIComponent(tag)}`),
  makeDrills: (tag: string) => request<TrialDrill[]>("/api/trial/drills", json({ tag })),
  checkDrill: (id: number, code: string) => request<DrillCheck>(`/api/trial/drills/${id}/check`, json({ code })),
  tracks: () => request<TrackSummary[]>("/api/tracks"),
  track: (id: string) => request<TrackDetail>(`/api/tracks/${id}`),
  lesson: (track: string, slug: string) => request<Lesson>(`/api/lessons/${track}/${slug}`),
  setProgress: (lessonId: string, status: Status) =>
    request<{ status: Status }>(`/api/progress/${lessonId}`, json({ status })),
  submitQuiz: (lessonId: string, answers: number[][]) =>
    request<QuizResult>(`/api/quiz/${lessonId}`, json({ answers })),
  runCode: (lessonId: string, exerciseId: string, code: string | File) => {
    const form = new FormData();
    if (typeof code === "string") form.append("code", code);
    else form.append("file", code);
    return request<RunResult>(`/api/practice/${lessonId}/${exerciseId}`, { method: "POST", body: form });
  },
  setProjectDir: (track: string, project_dir: string) =>
    request<{ project_dir: string }>(`/api/settings/project-dir/${track}`, { ...json({ project_dir }), method: "PUT" }),
  aiSettings: () => request<AISettings>("/api/settings/claude"),
  setAISettings: (body: { use: AIUse; model?: string; effort?: string }) =>
    request<AISettings>("/api/settings/claude", { ...json(body), method: "PUT" }),
  checkProject: (lessonId: string) => request<CheckResult>(`/api/project/${lessonId}/check`, { method: "POST" }),
  doubts: () => request<Doubt[]>("/api/doubts"),
  addDoubt: (lessonId: string, body: { location: string; anchor?: string | null; note: string }) =>
    request<Doubt>(`/api/doubts/${lessonId}`, json(body)),
  updateDoubt: (id: number, body: { note?: string; resolved?: boolean }) =>
    request<Doubt>(`/api/doubts/${id}`, { ...json(body), method: "PATCH" }),
  deleteDoubt: (id: number) => request(`/api/doubts/${id}`, { method: "DELETE" }),
  note: (lessonId: string) => request<NoteState>(`/api/notes/${lessonId}`),
  saveNote: (lessonId: string, body: string, chat_cursor?: number) =>
    request<NoteState>(`/api/notes/${lessonId}`, { ...json({ body, chat_cursor }), method: "PUT" }),
  trackNotes: (track: string) => request<TrackNotes>(`/api/notes/${track}`),
  roadmap: (on?: string | null) => request<Roadmap>(`/api/roadmap${on ? `?on=${on}` : ""}`),
  markTask: (id: string, done: boolean) =>
    request<RoadmapTask>(`/api/roadmap/tasks/${id}`, { ...json({ done }), method: "PUT" }),
  clearChat: (lessonId: string) => request(`/api/chat/${lessonId}`, { method: "DELETE" }),
};

/** Fetches a streamed plain-text response, calling onText with the full text so far. */
export async function streamText(path: string, init: RequestInit | undefined, onText: (full: string) => void) {
  const res = await fetch(API + path, init);
  if (!res.ok || !res.body) throw new Error(`Request failed: ${res.status}`);
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let full = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    full += decoder.decode(value, { stream: true });
    onText(full);
  }
  return full;
}

/** Coach for the trial room: streams a comment-only plan. `attempt` (1-3) is the hint level. */
export const streamCoach = (code: string, output: string, attempt: number, onText: (full: string) => void) => {
  const form = new FormData();
  form.append("code", code);
  form.append("output", output);
  form.append("attempt", String(attempt));
  return streamText("/api/trial/coach", { method: "POST", body: form }, onText);
};

export type TrialTurn = { role: "user" | "assistant"; content: string };

/** Free question in the trial room. Claude sees the code and the last output, plus the earlier turns. */
export const streamTrialChat = (
  message: string,
  code: string,
  output: string,
  history: TrialTurn[],
  onText: (full: string) => void,
) => streamText("/api/trial/chat", json({ message, code, output, history }), onText);

/** Coach on an exercise: comment-only hint at `level` (1-3). */
export const streamExerciseCoach = (
  lessonId: string,
  exerciseId: string,
  code: string,
  output: string,
  level: number,
  onText: (full: string) => void,
) => {
  const form = new FormData();
  form.append("code", code);
  form.append("output", output);
  form.append("level", String(level));
  return streamText(`/api/practice/${lessonId}/${exerciseId}/coach`, { method: "POST", body: form }, onText);
};

/** Step-by-step walkthrough (no solution code). The server refuses it (403) until Dev is really stuck. */
export const streamWalkthrough = (
  lessonId: string,
  exerciseId: string,
  code: string,
  output: string,
  onText: (full: string) => void,
) => {
  const form = new FormData();
  form.append("code", code);
  form.append("output", output);
  return streamText(`/api/practice/${lessonId}/${exerciseId}/walkthrough`, { method: "POST", body: form }, onText);
};

export const streamReview = (submissionId: number, onText: (full: string) => void) =>
  streamText(`/api/practice/review/${submissionId}`, undefined, onText);

export const streamProjectReview = (checkId: number, onText: (full: string) => void) =>
  streamText(`/api/project/review/${checkId}`, undefined, onText);

/** Streams a new or merged note. Nothing is saved until the learner presses Save. */
export const streamNotes = (lessonId: string, upto: number, onText: (full: string) => void, signal?: AbortSignal) =>
  streamText(`/api/notes/${lessonId}/generate?upto=${upto}`, { method: "POST", signal }, onText);

const onParam = (on?: string | null, first = "?") => (on ? `${first}on=${on}` : "");

/** Haiku's briefing for the plan: what to do now, how, what to watch. */
export const streamGuide = (
  onText: (full: string) => void,
  on?: string | null,
  fresh = false,
  signal?: AbortSignal,
) => streamText(`/api/roadmap/guide${fresh ? "?fresh=true" : ""}${onParam(on, fresh ? "&" : "?")}`, { signal }, onText);

/** Ask Haiku a question about the plan or today's task. */
export const streamPlanAsk = (question: string, onText: (full: string) => void, on?: string | null) =>
  streamText(`/api/roadmap/ask${onParam(on)}`, json({ question }), onText);

export const notesExportUrl = (track: string) => `${API}/api/notes/${track}/export.md`;

/** A screenshot attached to a chat message: raw base64 (no "data:" prefix). */
export type ChatImage = { media_type: string; data: string };

export const streamChat = (
  lessonId: string,
  message: string,
  onText: (full: string) => void,
  signal?: AbortSignal,
  images: ChatImage[] = [],
) => streamText(`/api/chat/${lessonId}`, { ...json({ message, images }), signal }, onText);

/** Lets the top bar refresh its % after progress changes anywhere on the page. */
export const PROGRESS_EVENT = "learner:progress";
export const notifyProgress = () => window.dispatchEvent(new Event(PROGRESS_EVENT));

/** Lets the sidebar and the top bar's revise list refresh after doubts change. */
export const DOUBTS_EVENT = "learner:doubts";
export const notifyDoubts = () => window.dispatchEvent(new Event(DOUBTS_EVENT));

/** Fired when a chat answer finishes, so "Update notes" can show there is new chat to add. */
export const CHAT_EVENT = "learner:chat";
export const notifyChat = () => window.dispatchEvent(new Event(CHAT_EVENT));
