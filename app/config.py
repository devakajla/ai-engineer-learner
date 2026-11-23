from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
DATA_DIR = ROOT / "data"
DB_URL = f"sqlite+aiosqlite:///{DATA_DIR / 'learner.db'}"
# Claude runs here so it never reads or edits the project itself.
CLAUDE_CWD = DATA_DIR / "claude_workspace"
# Screenshots pasted into the chat (served back so saved chats still show them).
CHAT_IMAGES_DIR = DATA_DIR / "chat_images"

TEST_TIMEOUT_SECONDS = 10
# Project checks run inside the learner's own uv env; the first run may install packages.
PROJECT_TEST_TIMEOUT_SECONDS = 120
DEFAULT_PROJECT_DIR = str(Path.home() / "Projects" / "taskflow")
# Tracks whose project is not TaskFlow: (project name, default folder).
TRACK_PROJECTS = {
    "genai": ("DevDocs Copilot", str(Path.home() / "Projects" / "devdocs-copilot")),
}


def project_name(track_id: str) -> str:
    return TRACK_PROJECTS.get(track_id, ("TaskFlow", ""))[0]


def default_project_dir(track_id: str) -> str:
    return TRACK_PROJECTS.get(track_id, ("", DEFAULT_PROJECT_DIR))[1]
# Models and effort levels the learner can pick in the UI (stored in the settings table).
CLAUDE_MODELS = {
    "claude-haiku-5-5": "Haiku 5.5",
    "claude-sonnet-5-5": "Sonnet 5.5",
    "claude-opus-5-5": "Opus 5.5",
}
CLAUDE_EFFORTS = ["low", "medium", "high", "xhigh", "max"]
# Each use of Claude has its own model + effort. Reviews have a fixed short format,
# so the cheaper Haiku handles them well; chat gets Sonnet.
CLAUDE_USES = ["chat", "review"]
CLAUDE_DEFAULTS = {
    "chat": ("claude-sonnet-5-5", "medium"),
    "review": ("claude-haiku-5-5", "medium"),
}

TRACK_ORDER = ["python", "fastapi", "dsa", "genai", "agentic"]
FRONTEND_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
