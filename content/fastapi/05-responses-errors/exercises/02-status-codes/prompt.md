# Correct status codes

Implement a tiny in-memory **bookmarks** API with the right status codes. Use the provided `BookmarkCreate` and `BOOKMARKS` dict.

| Request | Success | Errors |
|---|---|---|
| `POST /bookmarks` | **201**, returns `{"id": ..., "url": ..., "title": ...}` | **409** `{"detail": "Bookmark already exists"}` if the same `url` is already saved |
| `DELETE /bookmarks/{bookmark_id}` | **204**, empty body | **404** `{"detail": "Bookmark not found"}` |

Ids start at 1 and increase. Use `status.HTTP_...` constants.
