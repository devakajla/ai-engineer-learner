---
title: "Awareness: beyond text (images, audio, video)"
summary: See how models read images, hear audio and make pictures, how an image is sent in a message, what it costs, and where these models fail.
plan_ids: []
---

So far the model read text and wrote text. Many models can now do more. This is an **awareness** lesson: short and practical. You will learn the map of what exists, how to send an image to a model, and what to watch out for. No deep theory.

A model that works with more than text is **multimodal**. A **modality** is one kind of data: text, image, audio, video.

## The map

| Direction | What it does | Example |
| --- | --- | --- |
| Image in, text out | **Vision**: describe a photo, read a screenshot, answer about a chart | "What error is shown in this screenshot?" |
| Audio in, text out | **Speech to text** (STT, also called transcription) | A meeting recording becomes text |
| Text in, audio out | **Text to speech** (TTS) | A voice reads an answer aloud |
| Text in, image out | **Image generation** | "A red bicycle on the moon" |
| Video in | Frames and sound are analysed | Summarize a lecture video |
| Anything in, vector out | **Multimodal embeddings** | Search photos by a text description |

The most useful for an AI Engineer today: **vision** (documents, screenshots, receipts) and **speech to text** (voice apps).

## How does a model "see"?

The picture is cut into small squares called **patches**. Each patch is turned into numbers, a bit like a token. The model then reads these image tokens together with your text tokens, in the same context window (lesson 2).

Two results of this:

1. **A picture costs tokens.** A big image can cost hundreds or thousands of input tokens. Many providers resize large images first.
2. **Small details can be lost.** Tiny text, thin lines and exact counting are hard.

## Sending an image in a message

In lesson 4 a message had `content` as text. For vision, `content` becomes a **list of parts**. Each part says what it is:

```python
message = {
    "role": "user",
    "content": [
        {"type": "text", "text": "What is in this picture?"},
        {"type": "image_url", "image_url": {"url": "https://example.com/cat.jpg"}},
    ],
}
```

The `url` can be a web address, or a **data URL**: the image itself written as text inside the URL. A data URL has this shape:

```
data:image/png;base64,iVBORw0KGgo...
```

**Base64** is a way to write any bytes (like a picture file) using only normal letters and digits. Python can do it:

```python
import base64

data = b"hello"
print(base64.b64encode(data).decode())   # -> aGVsbG8=
```

`b"hello"` is **bytes** (raw data, not text). `b64encode` gives bytes again, and `.decode()` turns them into a normal string.

Let's practise the shape with a different example: a function that makes a "photo tag" message. Steps:

1. Make a list with the text part.
2. Add the other part.
3. Return the message dictionary with the role and the list.

```python
def note_message(text, extra):
    parts = [{"type": "text", "text": text}]
    parts.append({"type": "note", "note": extra})
    return {"role": "user", "content": parts}

note_message("Look", "blue")
# -> {'role': 'user', 'content': [{'type': 'text', 'text': 'Look'}, {'type': 'note', 'note': 'blue'}]}
```

The first exercise has the same shape, with an image part.

> Which models accept images, and the exact format, depends on the provider. Groq lists its vision models on `console.groq.com/docs/models`. Check the docs before you use one.

## Audio: speech to text

A speech model takes an audio file and returns text. With Groq it is a separate call (not `chat.completions`). Check the docs for the current model name and call.

The text you get can then go into your normal text pipeline: summarize it, search it, ask questions. A **voice assistant** is a chain: speech to text, then the LLM, then text to speech.

## Where multimodal models fail

- **Reading small or blurry text.** They guess. Check important numbers.
- **Counting and exact positions.** "How many chairs?" is often wrong.
- **Charts.** They may read the shape right and the numbers wrong.
- **Hallucination.** They can describe things that are not in the picture.
- **Privacy.** A photo can hold faces, addresses, ID numbers. You send it to a third party. Think before you do.
- **Cost and speed.** Images add tokens and delay.

For clean **documents**, a normal OCR tool or the PDF text layer is often cheaper and more exact than a vision model. Use vision when layout and pictures matter.

## Try it live

1. Pick a vision model from the Groq models page. Send it a photo by URL with a question. Print the answer.
2. Send a screenshot of an error message from your own terminal. Does it read the error correctly?
3. Make a data URL from a small local image (you build the function in exercise 2) and send that instead.
4. Look at `usage.prompt_tokens` for the call with and without the image. How many tokens did the image cost?

## A little deeper

- **Native multimodal.** Newer models are trained on text and images together from the start, so they mix the two better than older "glue" systems.
- **Multimodal RAG.** You can embed images (CLIP-style models) and search them with a text question. Or you turn every image into a text description first and index the text.
- **Diffusion models** are the usual kind of image generator. They start from noise and remove it step by step, guided by the text.
- **Structured output from images.** Vision plus JSON mode (lesson 9) gives you invoices and forms as data. Always validate (lesson 10).
- **Video** is usually handled by taking a few frames per second, plus the audio as text.
- **Safety.** Images can carry injection too: text inside a picture can give the model orders (lesson 37).

## Common mistakes

- Sending huge images when a smaller one is enough.
- Trusting numbers a vision model read from a chart.
- Putting a local file path in `url`. The API cannot see your disk. Use a web URL or a data URL.
- Forgetting that `content` is a list for vision messages.
- Sending private photos without thinking about where they go.

## Interview corner

**What is a multimodal model?**
A model that takes or produces more than one kind of data, such as text and images. Images are turned into tokens (patches) that the model reads together with text.

**How do you send an image to a chat model?**
Make the message `content` a list of parts: a text part and an `image_url` part. The URL can be a web address or a base64 data URL.

**What are the weak points of vision models?**
Small text, exact counting, reading numbers from charts, and hallucinating details. Check important values.

**When would you not use a vision model for a document?**
When OCR or the text layer of the PDF gives the text directly. It is cheaper, faster and more exact.

## Summary

- Multimodal means more than text: vision, speech to text, text to speech, image generation, video.
- An image is cut into patches and becomes tokens. It costs input tokens.
- A vision message has `content` as a list of parts: `{"type": "text", ...}` and `{"type": "image_url", ...}`.
- A data URL is `data:<mime>;base64,<text>`.
- Vision models can hallucinate and misread small details. Check what matters.
- Reference: `reference/genai-groq.md`.
