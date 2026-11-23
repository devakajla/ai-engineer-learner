# Build an image message

Write `image_message(text, image_url)`. It returns a `user` message that holds a question and one image.

Rules:
- The result is `{"role": "user", "content": [text part, image part]}`.
- The text part is `{"type": "text", "text": text}`.
- The image part is `{"type": "image_url", "image_url": {"url": image_url}}`.
- The text part comes first.

```python
image_message("What is this?", "https://example.com/cat.jpg")
# -> {'role': 'user', 'content': [
#      {'type': 'text', 'text': 'What is this?'},
#      {'type': 'image_url', 'image_url': {'url': 'https://example.com/cat.jpg'}}]}
```
