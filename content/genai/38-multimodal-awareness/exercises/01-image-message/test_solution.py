from solution import image_message


def test_shape():
    assert image_message("What is this?", "https://x/cat.jpg") == {
        "role": "user",
        "content": [
            {"type": "text", "text": "What is this?"},
            {"type": "image_url", "image_url": {"url": "https://x/cat.jpg"}},
        ],
    }


def test_text_first():
    parts = image_message("a", "b")["content"]
    assert parts[0]["type"] == "text" and parts[1]["type"] == "image_url"
