# Given from the first exercise. Do not change it.
import json


def parse_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


# Your task:
def ask_json(client, question):
    ...
