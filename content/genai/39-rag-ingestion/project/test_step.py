"""Step 15 checks. Runs with the current directory = the learner's project folder."""

import json
import uuid

from copilot.store import open_collection, search
from copilot.sync import clean_text, content_hash, load_manifest, plan_sync, save_manifest, sync_folder


class CountingEmbed:
    """Fake embedder that remembers every text it was asked to embed."""

    def __init__(self):
        self.texts = []

    def __call__(self, texts):
        self.texts.extend(texts)
        return [[t.lower().count("task"), t.lower().count("login"), 0.1] for t in texts]


def new_collection():
    return open_collection(None, name=f"t{uuid.uuid4().hex}")


def write(folder, name, text):
    (folder / name).write_text(text, encoding="utf-8")


def sources(collection):
    return sorted({m["source"] for m in collection.get()["metadatas"]})


def test_clean_text():
    raw = "Para one is\r\nhere,  with   spaces.\n\n\n\n12\nA hyphen-\nated word.\n\n  Last line  \n"
    assert clean_text(raw) == "Para one is\nhere, with spaces.\n\nA hyphenated word.\n\nLast line"
    assert clean_text("") == "" and clean_text("   \n\n  ") == ""
    assert clean_text("page\n7\ntext") == "page\ntext", "a line with only digits is a page number"
    assert clean_text("Version 2 is out") == "Version 2 is out", "digits inside a line stay"


def test_content_hash():
    assert content_hash("a  b\n c") == content_hash("a b c")
    assert content_hash("a b") != content_hash("a c")
    assert len(content_hash("x")) == 16


def test_plan_sync():
    stored = {"same.md": content_hash("one"), "changed.md": content_hash("old"), "gone.md": content_hash("x")}
    docs = {"same.md": "one", "changed.md": "new", "new.md": "hello"}
    assert plan_sync(stored, docs) == {
        "add": ["new.md"],
        "update": ["changed.md"],
        "delete": ["gone.md"],
        "same": ["same.md"],
    }
    assert plan_sync({}, {}) == {"add": [], "update": [], "delete": [], "same": []}


def test_manifest_round_trip(tmp_path):
    path = tmp_path / "manifest.json"
    assert load_manifest(path) == {}
    save_manifest(path, {"b.md": "2", "a.md": "1"})
    assert load_manifest(path) == {"a.md": "1", "b.md": "2"}
    assert list(json.loads(path.read_text())) == ["a.md", "b.md"], "keys are sorted so diffs stay small"


def test_first_sync_adds_everything(tmp_path):
    write(tmp_path, "tasks.md", "# Tasks\n\ncreate a task with POST")
    write(tmp_path, "auth.md", "# Auth\n\nlogin with a token")
    collection, manifest, embed = new_collection(), {}, CountingEmbed()
    report = sync_folder(collection, tmp_path, manifest, embed=embed)
    assert report == {"added": 2, "updated": 0, "deleted": 0, "same": 0, "chunks": 2}
    assert sources(collection) == ["auth.md", "tasks.md"]
    assert set(manifest) == {"auth.md", "tasks.md"}


def test_second_sync_embeds_nothing(tmp_path):
    write(tmp_path, "tasks.md", "# Tasks\n\ncreate a task with POST")
    collection, manifest, embed = new_collection(), {}, CountingEmbed()
    sync_folder(collection, tmp_path, manifest, embed=embed)
    before = len(embed.texts)
    report = sync_folder(collection, tmp_path, manifest, embed=embed)
    assert report == {"added": 0, "updated": 0, "deleted": 0, "same": 1, "chunks": 0}
    assert len(embed.texts) == before, "unchanged files must not be embedded again (that costs money)"


def test_changed_and_deleted_files(tmp_path):
    write(tmp_path, "tasks.md", "# Tasks\n\ncreate a task with POST")
    write(tmp_path, "auth.md", "# Auth\n\nlogin with a token")
    collection, manifest, embed = new_collection(), {}, CountingEmbed()
    sync_folder(collection, tmp_path, manifest, embed=embed)
    write(tmp_path, "tasks.md", "# Tasks\n\ndelete a task with DELETE")
    (tmp_path / "auth.md").unlink()
    embed.texts.clear()
    report = sync_folder(collection, tmp_path, manifest, embed=embed)
    assert report["updated"] == 1 and report["deleted"] == 1 and report["added"] == 0
    assert sources(collection) == ["tasks.md"], "the removed file must leave the index"
    assert set(manifest) == {"tasks.md"}
    assert len(embed.texts) == 1, "only the changed file is embedded"
    texts = collection.get()["documents"]
    assert all("create a task" not in t for t in texts), "old chunks of a changed file must be gone"
    assert search(collection, "delete", k=1, embed=embed)[0]["source"] == "tasks.md"


def test_formatting_only_change_is_not_an_update(tmp_path):
    write(tmp_path, "tasks.md", "# Tasks\n\ncreate a task")
    collection, manifest, embed = new_collection(), {}, CountingEmbed()
    sync_folder(collection, tmp_path, manifest, embed=embed)
    write(tmp_path, "tasks.md", "# Tasks\r\n\r\n\r\ncreate   a task\r\n")
    assert sync_folder(collection, tmp_path, manifest, embed=embed)["same"] == 1
