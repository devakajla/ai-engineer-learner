# Given from earlier exercises. Do not change these.
import json

def ask(client, prompt, system=None, temperature=0):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b", messages=messages, temperature=temperature
    )
    return response.choices[0].message.content.strip()


# Your task:
def extract_facts(client, message):
    reply = ask(
        client,
        "List the lasting facts about the user in this message as a JSON list of short strings. "
        "Reply with the JSON list only. Use [] if there are none.\n\n" + message,
    )
    start, end = reply.find("["), reply.rfind("]")
    if start == -1 or end < start:
        return []
    try:
        data = json.loads(reply[start : end + 1])
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [item.strip() for item in data if isinstance(item, str) and item.strip()]
