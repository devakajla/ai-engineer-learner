# Ask about an image

Use your message builder with a model call. `image_message(text, image_url)` (exercise 1) is in the starter.

Write `describe_image(client, model, question, image_url)`.

Rules:
- Build the message with `image_message(question, image_url)`.
- Call `client.chat.completions.create(model=model, messages=[message], max_completion_tokens=300)`. The `model` is a parameter, because vision model names change.
- If `image_url` is empty, raise `ValueError("no image")` **before** any call.
- Return `response.choices[0].message.content`.

```python
describe_image(client, "some-vision-model", "What is in it?", "https://x/cat.jpg")
# -> 'A cat on a sofa.'
```
