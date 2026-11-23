# Given from exercise 1. Do not change this.
def image_message(text, image_url):
    return {
        "role": "user",
        "content": [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": image_url}},
        ],
    }


# Your task:
def describe_image(client, model, question, image_url):
    ...
