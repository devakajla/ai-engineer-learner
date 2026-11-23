"""Checks every track, lesson, quiz and exercise under content/.

- track.yaml parses; slugs are unique; refs point at real lessons
- lesson.md has front matter with a title
- quiz answers are valid indices; single-choice has exactly one answer
- videos.yaml segments point at real exercises with start < end
- every exercise has its 4 files; solution.py passes its tests; starter.py fails them
- every project step with test_step.py has a reference solution/ that passes it,
  and an empty project folder fails it

Usage: uv run python scripts/validate_content.py [track/slug ...]
"""

import asyncio
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import CONTENT_DIR  # noqa: E402
from app.content import get_tracks, load_videos, read_front_matter  # noqa: E402
import tempfile  # noqa: E402

from app.services.runner import run_project_tests, run_tests  # noqa: E402

REQUIRED_EX_FILES = ["prompt.md", "starter.py", "solution.py", "test_solution.py"]


def check_quiz(path: Path, errors: list[str]) -> int:
    items = yaml.safe_load(path.read_text()) or []
    for i, item in enumerate(items, 1):
        where = f"{path.relative_to(CONTENT_DIR)} Q{i}"
        missing = {"q", "options", "answer"} - item.keys()
        if missing:
            errors.append(f"{where}: missing {missing}")
            continue
        n = len(item["options"])
        ans = item["answer"]
        if not isinstance(ans, list) or not ans:
            errors.append(f"{where}: answer must be a non-empty list")
            continue
        if any(not isinstance(a, int) or a < 0 or a >= n for a in ans):
            errors.append(f"{where}: answer index out of range {ans} (options: {n})")
        if item.get("type", "single") == "single" and len(ans) != 1:
            errors.append(f"{where}: single-choice must have exactly one answer")
        if item.get("type", "single") not in {"single", "multi"}:
            errors.append(f"{where}: type must be single or multi")
        if not item.get("explain"):
            errors.append(f"{where}: missing explain")
    return len(items)


async def check_exercise(ex_dir: Path, errors: list[str]) -> None:
    where = ex_dir.relative_to(CONTENT_DIR)
    missing = [f for f in REQUIRED_EX_FILES if not (ex_dir / f).exists()]
    if missing:
        errors.append(f"{where}: missing {missing}")
        return
    good = await run_tests((ex_dir / "solution.py").read_text(), ex_dir, timeout=30)
    if not good.passed:
        errors.append(f"{where}: solution.py FAILS its tests\n{good.output[-1500:]}")
    bad = await run_tests((ex_dir / "starter.py").read_text(), ex_dir)
    if bad.passed:
        errors.append(f"{where}: starter.py PASSES the tests (tests too weak?)")


async def check_project_step(step_dir: Path, errors: list[str]) -> None:
    where = step_dir.relative_to(CONTENT_DIR)
    test = step_dir / "test_step.py"
    if not test.exists():
        return
    solution = step_dir / "solution"
    if not solution.is_dir():
        errors.append(f"{where}: has test_step.py but no solution/ reference project")
        return
    good = await run_project_tests(solution, test, timeout=60, use_uv=False)
    if not good.passed:
        errors.append(f"{where}: reference solution/ FAILS test_step.py\n{good.output[-1500:]}")
    with tempfile.TemporaryDirectory() as empty:
        bad = await run_project_tests(Path(empty), test, timeout=60, use_uv=False)
    if bad.passed:
        errors.append(f"{where}: test_step.py passes on an EMPTY folder (tests too weak?)")


async def main(only: list[str]) -> int:
    errors: list[str] = []
    tracks = get_tracks()
    lessons = exercises = questions = steps = 0

    for track in tracks.values():
        seen: set[str] = set()
        for ref in track.lessons:
            if ref.id in seen:
                errors.append(f"{track.id}/track.yaml: duplicate entry {ref.id}")
            seen.add(ref.id)

    for track_dir in sorted(p for p in CONTENT_DIR.iterdir() if p.is_dir()):
        listed = {r.slug for r in tracks.get(track_dir.name).lessons} if track_dir.name in tracks else set()
        for lesson_dir in sorted(p for p in track_dir.iterdir() if p.is_dir()):
            lid = f"{track_dir.name}/{lesson_dir.name}"
            if only and lid not in only:
                continue
            if lesson_dir.name not in listed:
                errors.append(f"{lid}: folder exists but is not listed in track.yaml")
            md = lesson_dir / "lesson.md"
            if not md.exists():
                errors.append(f"{lid}: missing lesson.md")
                continue
            try:
                meta, body = read_front_matter(md.read_text())
            except yaml.YAMLError as e:
                errors.append(f"{lid}: bad front matter YAML: {e}")
                continue
            if not meta.get("title"):
                errors.append(f"{lid}: lesson.md front matter has no title")
            if len(body.strip()) < 200:
                errors.append(f"{lid}: lesson body looks empty")
            lessons += 1
            if (lesson_dir / "quiz.yaml").exists():
                try:
                    questions += check_quiz(lesson_dir / "quiz.yaml", errors)
                except yaml.YAMLError as e:
                    errors.append(f"{lid}: bad quiz.yaml: {e}")
            ex_root = lesson_dir / "exercises"
            if ex_root.is_dir():
                ex_dirs = sorted(p for p in ex_root.iterdir() if p.is_dir())
                await asyncio.gather(*(check_exercise(d, errors) for d in ex_dirs))
                exercises += len(ex_dirs)
            if (lesson_dir / "videos.yaml").exists():
                try:
                    _, segs = load_videos(lesson_dir)
                except (yaml.YAMLError, KeyError, ValueError) as e:
                    errors.append(f"{lid}: bad videos.yaml: {e!r}")
                    segs = {}
                for slug, v in segs.items():
                    if not (ex_root / slug).is_dir():
                        errors.append(f"{lid}/videos.yaml: segment for unknown exercise {slug!r}")
                    if v.end is not None and v.end <= v.start:
                        errors.append(f"{lid}/videos.yaml: {slug} end must be after start")
            if (lesson_dir / "project" / "step.md").exists():
                await check_project_step(lesson_dir / "project", errors)
                steps += 1

    print(f"Checked {lessons} lessons, {questions} quiz questions, {exercises} exercises, {steps} project steps.")
    if errors:
        print(f"\n{len(errors)} problem(s):")
        for e in errors:
            print(" ✗", e)
        return 1
    print("All good ✓")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv[1:])))
