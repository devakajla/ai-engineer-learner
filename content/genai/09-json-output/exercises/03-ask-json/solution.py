import json


def parse_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def ask_json(client, question):
    messages = [
        {"role": "system", "content": "Reply with JSON only."},
        {"role": "user", "content": question},
    ]
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0,
    )
    return parse_json(response.choices[0].message.content)
