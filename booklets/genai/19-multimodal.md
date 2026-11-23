# 19. Multimodal basics: images and audio

**Modality** means a kind of data: text, image, audio, video. A **multimodal** model understands more than one. Many modern models read images, and some also hear and speak.

> Honesty note: the calls in this chapter were not run here. Image and audio support and the exact message formats vary by provider and model. Check your provider's docs.

## Vision: sending an image

A vision model gets the image as part of a user message. Most APIs accept either a **URL** or the image **encoded as base64** text. A common message shape:

```python
messages = [{
    "role": "user",
    "content": [
        {"type": "text", "text": "What is in this picture? Answer in one sentence."},
        {"type": "image_url", "image_url": {"url": "https://example.com/cat.jpg"}},
    ],
}]
```

The difference from earlier chapters: `content` is a **list of parts**, instead of a plain string. Each part has a `type`.

For a local file, turn it into a **data URL**:

```python
import base64

def to_data_url(path, mime="image/png"):
    with open(path, "rb") as file:
        encoded = base64.b64encode(file.read()).decode("ascii")
    return f"data:{mime};base64,{encoded}"

print(to_data_url("/dev/null")[:22])
# -> data:image/png;base64,
```

(We used an empty file to show the prefix. Real images give long text.) Base64 turns bytes into plain letters, and makes the data about one third bigger.

### Uses of vision

- Read text in screenshots, receipts, forms, charts (this is often called OCR-like use).
- Describe or classify photos.
- Understand diagrams and UI screens.
- Extract structured data from a document image (combine with chapter 7).

### Cost and limits

Images **cost tokens**, and a large image can cost as much as many words. Resize large pictures before sending. Models can misread small text, count objects wrongly, or miss fine detail. Treat outputs as untrusted, validate like any other.

## Audio

Two jobs you will meet:

- **Speech to text** (transcription, for example Whisper models): audio in, text out. Groq hosts Whisper-style models, so `client.audio` exists in the SDK. Check the docs for the current model names and file limits.
- **Text to speech:** text in, audio out.

A **voice assistant** chains them: speech to text, then an LLM, then text to speech.

@@ flow | Figure 19.1: a voice assistant.
Microphone|audio|blue -> Speech to text|transcript|yellow -> LLM or RAG|answer text|green -> Text to speech|audio out|purple
@@ end

The main engineering problem is **latency**. Each step adds delay, so people stream every stage and keep the model small.

## Embeddings for images

An embedding model can map **images and text into the same space** (CLIP is the famous example). Then a text query like "red running shoes" can be compared with **image vectors**, and you can search a photo library with words, or find similar pictures.

```
text "a red shoe"  ->  vector
photo of a shoe    ->  vector      (same model, same space)
cosine(text, photo) is high when they match
```

The rest of the machinery (vector database, cosine, filters) is **exactly the same** as for text, from chapters 10 and 12. Only the embedding model changes.

## Multimodal RAG (the idea)

Documents hold charts, tables and pictures. Two approaches:

1. **Convert to text first:** describe each image with a vision model and index the description. Simple, and works with your current stack.
2. **Embed the images directly** with a multimodal embedder, and retrieve images. Then send the image to a vision model for the answer.

Start with the first. It reuses everything you have.

::: {.box .checkpoint}
**Checkpoint:** you can show how an image is placed in a message, and explain why a shared text and image embedding space allows search by words.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Sending huge images and paying for the tokens.
- Trusting the reading of small text or numbers without checks.
- Forgetting the MIME type in a data URL.
- Putting raw base64 in logs.
- Expecting every model to accept images.
- Ignoring the privacy of photos and recordings.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: How do you send an image to an LLM?** As an image part in the message content, either a URL or a base64 data URL, next to a text part.

**Q: What is a multimodal embedding?** A model that maps different data types (text, image) into one vector space, so they are directly comparable.

**Q: How would you build search over product photos?** Embed images with a CLIP-style model, store the vectors in a vector database, and embed the text query with the same model.

**Q: What is the main challenge of a voice assistant?** End-to-end latency across transcription, generation and speech, solved with streaming and small models.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write `make_image_message(text, data_url)` that returns the message shape above, and test its keys.
2. Encode a small image file to a data URL and print its length.
3. Write the steps of a receipt reader that returns validated JSON (use chapter 7).
4. Draw the pipeline for a voice-driven support bot with RAG.
5. **Think:** why is converting images to text descriptions a good first step for multimodal RAG?
:::
