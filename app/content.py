"""Loads the curriculum from content/ into an ordered tree.

Layout (see CLAUDE.md for the authoring rules):
    content/<track>/track.yaml                 ordered levels -> lessons
    content/<track>/<slug>/lesson.md           theory, with YAML front matter
    content/<track>/<slug>/quiz.yaml           optional
    content/<track>/<slug>/videos.yaml         optional: intro video + per-exercise video segments
    content/<track>/<slug>/exercises/<ex>/     prompt.md, starter.py, solution.py, test_solution.py
    content/<track>/<slug>/project/            step.md, test_step.py, solution/ (reference project at this step)

A lesson listed in track.yaml without a folder is shown as "coming soon".
Markdown is returned as-is; the frontend renders it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

from app.config import CONTENT_DIR, TRACK_ORDER


@dataclass
class Video:
    """A YouTube video, or one segment of it (start/end in seconds)."""

    video_id: str
    title: str
    start: int = 0
    end: int | None = None


@dataclass
class Exercise:
    id: str
    title: str
    prompt: str  # markdown, without the "# Title" line
    starter: str
    dir: Path
    video: Video | None = None


@dataclass
class ProjectStep:
    """One step of the track's running project, checked against the learner's own folder."""

    title: str
    instructions: str  # markdown, without the "# Title" line
    test_file: Path | None
    dir: Path


@dataclass
class Question:
    q: str  # markdown
    type: str  # single | multi
    options: list[str]  # markdown (inline)
    answer: list[int]
    explain: str


@dataclass
class LessonRef:
    """An entry in the sidebar."""

    track: str
    slug: str
    title: str
    kind: str = "lesson"  # lesson | interview
    available: bool = False

    @property
    def id(self) -> str:
        return f"{self.track}/{self.slug}"


@dataclass
class Level:
    id: str
    title: str
    lessons: list[LessonRef] = field(default_factory=list)


@dataclass
class Track:
    id: str
    title: str
    levels: list[Level]

    @property
    def lessons(self) -> list[LessonRef]:
        return [lesson for level in self.levels for lesson in level.lessons]


@dataclass
class Lesson:
    ref: LessonRef
    title: str
    summary: str
    plan_ids: list[str]
    body: str  # markdown
    quiz: list[Question]
    exercises: list[Exercise]
    project: ProjectStep | None
    intro_video: Video | None = None


def read_front_matter(text: str) -> tuple[dict, str]:
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        return yaml.safe_load(fm) or {}, body.lstrip()
    return {}, text


def _video(item: dict) -> Video:
    return Video(
        video_id=item["video_id"],
        title=item.get("title", ""),
        start=int(item.get("start", 0)),
        end=int(item["end"]) if item.get("end") is not None else None,
    )


def load_videos(lesson_dir: Path) -> tuple[Video | None, dict[str, Video]]:
    """videos.yaml -> (intro video, {exercise slug: segment})."""
    path = lesson_dir / "videos.yaml"
    if not path.exists():
        return None, {}
    data = yaml.safe_load(path.read_text()) or {}
    intro = _video(data["intro"]) if data.get("intro") else None
    return intro, {seg["exercise"]: _video(seg) for seg in data.get("segments") or []}


def _load_exercises(lesson_dir: Path) -> list[Exercise]:
    segments = load_videos(lesson_dir)[1]
    ex_root = lesson_dir / "exercises"
    if not ex_root.is_dir():
        return []
    exercises = []
    for ex_dir in sorted(p for p in ex_root.iterdir() if p.is_dir()):
        prompt = (ex_dir / "prompt.md").read_text()
        first, _, rest = prompt.partition("\n")
        has_title = first.startswith("#")
        exercises.append(
            Exercise(
                id=ex_dir.name,
                title=first.lstrip("# ").strip() if has_title else ex_dir.name,
                prompt=rest.strip() if has_title else prompt,
                starter=(ex_dir / "starter.py").read_text(),
                dir=ex_dir,
                video=segments.get(ex_dir.name),
            )
        )
    return exercises


def _split_title(md: str, fallback: str) -> tuple[str, str]:
    first, _, rest = md.partition("\n")
    if first.startswith("#"):
        return first.lstrip("# ").strip(), rest.strip()
    return fallback, md


def _load_project(lesson_dir: Path) -> ProjectStep | None:
    step_dir = lesson_dir / "project"
    if not (step_dir / "step.md").exists():
        return None
    title, body = _split_title((step_dir / "step.md").read_text(), "Project step")
    test = step_dir / "test_step.py"
    return ProjectStep(title=title, instructions=body, test_file=test if test.exists() else None, dir=step_dir)


def _load_quiz(lesson_dir: Path) -> list[Question]:
    path = lesson_dir / "quiz.yaml"
    if not path.exists():
        return []
    items = yaml.safe_load(path.read_text()) or []
    return [
        Question(
            q=item["q"],
            type=item.get("type", "single"),
            options=[str(o) for o in item["options"]],
            answer=list(item["answer"]),
            explain=item.get("explain", ""),
        )
        for item in items
    ]


def _content_signature() -> float:
    """Latest mtime under content/, so edits show up without a restart."""
    return max((p.stat().st_mtime for p in CONTENT_DIR.rglob("*")), default=0.0)


@lru_cache(maxsize=2)
def _load_tracks(_sig: float) -> dict[str, Track]:
    tracks: dict[str, Track] = {}
    for track_id in TRACK_ORDER:
        path = CONTENT_DIR / track_id / "track.yaml"
        if not path.exists():
            continue
        data = yaml.safe_load(path.read_text())
        levels = [
            Level(
                id=lv["id"],
                title=lv["title"],
                lessons=[
                    LessonRef(
                        track=track_id,
                        slug=entry["slug"],
                        title=entry["title"],
                        kind=entry.get("kind", "lesson"),
                        available=(CONTENT_DIR / track_id / entry["slug"] / "lesson.md").exists(),
                    )
                    for entry in lv.get("lessons", [])
                ],
            )
            for lv in data.get("levels", [])
        ]
        tracks[track_id] = Track(id=track_id, title=data["title"], levels=levels)
    return tracks


@lru_cache(maxsize=256)
def _load_lesson(track: str, slug: str, _sig: float) -> Lesson | None:
    ref = find_ref(track, slug)
    path = CONTENT_DIR / track / slug / "lesson.md"
    if not ref or not path.exists():
        return None
    meta, body = read_front_matter(path.read_text())
    return Lesson(
        ref=ref,
        title=meta.get("title", ref.title),
        summary=meta.get("summary", ""),
        plan_ids=meta.get("plan_ids", []) or [],
        body=body,
        quiz=_load_quiz(path.parent),
        exercises=_load_exercises(path.parent),
        project=_load_project(path.parent),
        intro_video=load_videos(path.parent)[0],
    )


def get_tracks() -> dict[str, Track]:
    return _load_tracks(_content_signature())


def get_lesson(track: str, slug: str) -> Lesson | None:
    return _load_lesson(track, slug, _content_signature())


def find_ref(track: str, slug: str) -> LessonRef | None:
    t = get_tracks().get(track)
    return next((r for r in t.lessons if r.slug == slug), None) if t else None


def neighbours(ref: LessonRef) -> tuple[LessonRef | None, LessonRef | None]:
    lessons = get_tracks()[ref.track].lessons
    i = [r.id for r in lessons].index(ref.id)
    prev = lessons[i - 1] if i > 0 else None
    nxt = lessons[i + 1] if i + 1 < len(lessons) else None
    return prev, nxt
