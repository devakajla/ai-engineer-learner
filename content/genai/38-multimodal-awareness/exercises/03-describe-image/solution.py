# Given from exercise 1. Do not change this.
def image_message(text, image_url):
    return {
        "role": "user",
        "content": [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": image_url}},
        ],
    }


def describe_image(client, model, question, image_url):
    if not image_url:
        raise ValueError("no image")
    message = image_message(question, image_url)
    response = client.chat.completions.create(model=model, messages=[message], max_completion_tokens=300)
    return response.choices[0].message.content
