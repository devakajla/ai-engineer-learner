---
title: "RAG for real users: access control, tenants and freshness"
summary: Make sure each user only gets chunks they are allowed to see, keep customers separate, and keep answers from using old documents.
plan_ids: []
---

In a demo, one person asks questions about public docs. In a real company:

- Many **customers** (tenants) use the same app. Customer A must never see customer B's data.
- Inside one company, the HR files are for HR. The engineering docs are for engineers.
- Documents get old. An answer that uses last year's price is wrong.

This lesson is about these three problems. The first two are **security**: a bug there is a data leak, which can end a company.

## Why RAG leaks easily

Think about the path of a chunk:

```
search -> chunk -> prompt -> model -> answer -> user
```

If a chunk reaches the **prompt**, the model can say anything from it. The model cannot keep a secret from the user it is talking to. It only repeats what it was given. So the rule is:

> **A chunk the user may not see must never reach the prompt.**

Do **not** rely on a prompt rule like "do not show HR files to normal users". The model can be tricked (lesson 37), and it can make mistakes. The check must be **code**, applied **before** the model.

## Access control: who may see what

Every chunk gets **access metadata** during ingestion (lesson 39):

- `tenant`: which customer or company it belongs to.
- `groups`: which groups may read it (empty means everyone in the tenant).

Every user has a `tenant` and some `groups`. They come from your **login system** (an authentication token you verify on the server), not from the question and not from the model.

The rule, as a function:

1. Different tenant: **no**. Always.
2. Same tenant, chunk has no groups: yes.
3. Chunk has groups: yes only if the user has at least one of them.

Let's practise this kind of "all rules must pass" function with a different example: may a person enter a club?

1. A rule that fails returns `False` at once.
2. A club with no required badges is open to its members.
3. Otherwise, the person needs at least one of the badges.

```python
def may_enter(club, person):
    if club["city"] != person["city"]:
        return False
    badges = club.get("badges", [])
    if not badges:
        return True
    return any(badge in person.get("badges", []) for badge in badges)

may_enter({"city": "Pune", "badges": ["gold"]}, {"city": "Pune", "badges": ["gold", "blue"]})   # -> True
may_enter({"city": "Pune"}, {"city": "Delhi"})                                                   # -> False
```

`any(...)` is `True` when at least one item of the loop is true. `.get("badges", [])` gives an empty list when the key is missing, so a missing key does not crash the code. The first exercise has the same shape.

### Where to filter: before the search or after?

Two ways:

- **Pre-filter**: tell the vector database "search only chunks where `tenant == acme`". Good: the results are already allowed, and you get a full `k`. Chroma, pgvector and Qdrant can do this (lessons 17 and 19).
- **Post-filter**: search first, then remove the hits the user may not see. Risk: the top 10 may all be removed, and nothing is left. The fix is to **over-fetch**: ask for `k * 5` hits, filter, then cut to `k`.

For hard separation (tenants), prefer a **pre-filter** that you cannot forget. For fine rules (groups), a post-filter with over-fetch is often fine. You can use both: the tenant as a database filter, and groups as a post-filter.

## Multi-tenancy designs

| Design | How | Good | Bad |
| --- | --- | --- | --- |
| **One index per tenant** | Each customer has a separate collection or database | Strong separation, easy delete | Many indexes to manage, costs more |
| **One shared index with a `tenant` filter** | One collection, every query has a tenant filter | Simple, cheap | One missing filter is a leak |
| **Separate deployment** | Each big customer gets their own stack | Best isolation, custom rules | Most work and cost |

A common choice: a shared index with a **mandatory** tenant filter that is added in **one** place in your code (a wrapper around the search), so no developer can forget it. Test it: write a test that logs in as tenant B and tries to find tenant A's text.

The tenant must come from the **verified login**, never from a request field that the user can change.

## Permissions change

A person leaves a group. A file is moved to a private folder. Your index still has the old permissions. This is called **ACL drift** (ACL = access control list). Ways to handle it:

- Re-sync the permissions often (like the incremental update of lesson 39).
- Or check the permission in the **source system** at query time for the final hits.
- And delete the chunks of removed documents at once.

## Freshness: old answers are wrong answers

Each chunk should have `updated` (a date) from the source. Then:

- **Filter** out chunks older than some age (for example, news older than 30 days).
- **Boost** newer chunks a little, if documents have versions.
- **Prefer the latest version** of a document. Keep `version` metadata, and filter `version == latest`.
- **Delete** outdated documents, do not just stop linking to them (lesson 39: stale chunks).

Python can compare dates. A date text like `"2026-11-23"` becomes a date with `date.fromisoformat`. Subtracting two dates gives a `timedelta` whose `.days` is the number of days between them.

```python
from datetime import date

today = date.fromisoformat("2026-11-23")
then = date.fromisoformat("2026-11-13")
print((today - then).days)   # -> 10
```

Let's practise the "keep if recent enough" filter with a different example: keep the milk bottles that are not too old.

1. For each bottle, if it has no date, keep it (unknown).
2. Otherwise compute the age in days. Keep it when the age is at most the limit.

```python
def fresh_bottles(bottles, today, limit):
    today_date = date.fromisoformat(today)
    kept = []
    for bottle in bottles:
        bought = bottle.get("bought")
        if bought is None:
            kept.append(bottle)
            continue
        if (today_date - date.fromisoformat(bought)).days <= limit:
            kept.append(bottle)
    return kept

bottles = [{"id": 1, "bought": "2026-11-20"}, {"id": 2, "bought": "2026-10-01"}]
fresh_bottles(bottles, "2026-11-23", 7)   # -> [{'id': 1, 'bought': '2026-11-20'}]
```

You build the same filter for hits in the third exercise.

## Putting it together

The final search function has this shape:

1. Over-fetch from the search.
2. Remove what the user may not see.
3. Remove what is too old.
4. Cut to `k`.

This function is the **only door** between your index and the prompt. Test it hard, including the unhappy cases.

## Try it live

1. Index 6 short chunks with `tenant` and `groups` metadata (2 tenants, one HR-only chunk).
2. Write your `search_for_user`. Log in as each kind of user and ask the same question. Print which chunk ids came back.
3. Try to leak on purpose: as tenant B, ask for something only tenant A has. Prove you get *no* hits.
4. Add `updated` dates. Ask about something that has an old and a new version. Which one comes back with and without the freshness filter?

## A little deeper

- **Pre-filter and recall.** A very strict filter on an HNSW index can lower recall or slow the search (lesson 19). Test with your real filters.
- **Row-level security.** If you use pgvector, Postgres can enforce row-level security (a rule on the table), so even a buggy query cannot read other tenants' rows.
- **Embeddings can leak.** Vectors hold information about their text. Treat the vector store as sensitive as the documents.
- **Right to be forgotten.** When a person asks to delete their data, delete the chunks **and** the vectors, and any caches and logs that hold the text.
- **Audit logs.** Log who asked, which chunk ids were retrieved, and which were shown. When something goes wrong you can see what happened. Do not log secrets in plain text.
- **Per-user caches.** A cache of answers must be keyed by the user's access scope, or user A's cached answer can be served to user B.
- **Prompt injection in documents.** A chunk can contain instructions (lesson 37). Access control does not stop it. Wrap chunks as untrusted data.
- **PII.** Personal data (names, phone numbers, ID numbers) may need to be removed or masked before indexing.

## Common mistakes

- Trusting a prompt rule ("do not reveal HR data") instead of filtering in code.
- Taking the `tenant` from the request body or from the model.
- Filtering after the search without over-fetching, so users get empty or short results.
- A shared index where one forgotten filter leaks everything.
- Never updating permissions after the first ingestion.
- Caching answers across users.
- Freshness: no `updated` date in the metadata.

## Interview corner

**How do you stop a RAG app from leaking one user's data to another?**
Put access metadata (tenant, groups) on every chunk, take the user's identity from the verified login on the server, and filter in code before chunks reach the prompt. Prefer a pre-filter on the tenant, test with cross-tenant queries, and never rely on a prompt instruction.

**Pre-filtering or post-filtering?**
A pre-filter restricts the search itself and returns a full `k`. A post-filter removes hits afterwards and needs over-fetching. Use a pre-filter for hard boundaries like tenants.

**How do you design multi-tenant RAG?**
Options: an index per tenant (strong separation, more to manage), a shared index with a mandatory tenant filter in one wrapper (simple, needs care), or separate deployments for big customers. Choose by risk, scale and cost.

**How do you keep answers fresh?**
Store an updated date and version on each chunk, re-sync changed documents, delete removed ones, filter or boost by date, and prefer the latest version.

## Summary

- A chunk the user may not see must never reach the prompt. Filter in code, not in the prompt.
- Chunks carry `tenant` and `groups`. The user's identity comes from the verified login.
- Pre-filter for hard boundaries. Post-filter needs over-fetching (`k * 5`).
- Tenancy: index per tenant, shared index with a mandatory filter, or separate deployments.
- Permissions drift, so re-sync them and delete removed documents at once.
- Freshness: `updated` and `version` metadata, filter old chunks, prefer the latest version.
- One function is the only door between index and prompt. Test it with unhappy cases.
- Project: step 16 adds `copilot/access.py`: access control and freshness.
- Reference: `reference/genai-retrieval.md`.
