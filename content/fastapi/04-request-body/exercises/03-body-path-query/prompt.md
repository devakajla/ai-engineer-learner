# Body + path + query together

Create a `NoteUpdate` model (`text`: str 1–500 chars, `pinned`: bool default `False`) and the route:

`PUT /notes/{note_id}?notify=<bool>`

- `note_id`: int ≥ 1 (path)
- `notify`: bool, default `False` (query)
- body: `NoteUpdate`

Return:

```json
{"note_id": 5, "notify": true, "note": {"text": "Buy milk", "pinned": false}}
```
