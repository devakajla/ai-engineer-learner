# Accept an image upload, but check it

Create `app` with `POST /avatar`. The client sends one file in the form field `file`.

Rules, checked in this order:

1. The content type must be `image/png` or `image/jpeg`. Otherwise answer **415** with `{"detail": "Only PNG or JPEG images"}`.
2. The file must not be empty. An empty file gives **400** with `{"detail": "Empty file"}`.
3. The file must be at most **1024 bytes**. A bigger file gives **413** with `{"detail": "File too large"}`.

If everything is fine, answer **201** with:

```json
{"filename": "me.png", "content_type": "image/png", "size": 4}
```

`size` is the number of bytes you read. Use only the **base name** of the file name (no folders): a client may send `"../../etc/passwd.png"`, and you must answer with `"passwd.png"`.

```text
POST /avatar  file=me.png (image/png, 4 bytes)   -> 201 {"filename": "me.png", "content_type": "image/png", "size": 4}
POST /avatar  file=notes.txt (text/plain)        -> 415
POST /avatar  file=big.png (2000 bytes)          -> 413
```

**Think first:** Is it safe to trust `file.filename` and `file.content_type`? What could a client lie about?

**Hint:** `file: UploadFile`. Read the bytes with `data = file.file.read()` (use a plain `def` route). `os.path.basename(...)` or `Path(name).name` gives the base name. Read the data **once**, then check its length.
