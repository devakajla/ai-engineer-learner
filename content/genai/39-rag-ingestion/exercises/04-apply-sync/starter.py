import hashlib


# Given from earlier exercises. Do not change these.
def content_hash(text):
    normal = " ".join(text.split())
    return hashlib.sha256(normal.encode("utf-8")).hexdigest()[:16]


def plan_sync(stored, docs):
    plan = {"add": [], "update": [], "delete": [], "same": []}
    for doc_id in sorted(docs):
        if doc_id not in stored:
            plan["add"].append(doc_id)
        elif stored[doc_id] != content_hash(docs[doc_id]):
            plan["update"].append(doc_id)
        else:
            plan["same"].append(doc_id)
    for doc_id in sorted(stored):
        if doc_id not in docs:
            plan["delete"].append(doc_id)
    return plan


# Your task:
def apply_sync(index, docs, embed):
    ...
