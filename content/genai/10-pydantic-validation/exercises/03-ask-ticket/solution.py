from pydantic import BaseModel, Field, ValidationError


class Ticket(BaseModel):
    title: str = Field(min_length=1)
    priority: int = Field(ge=1, le=5)
    tags: list[str] = []


def ask_ticket(client, text, max_tries=3):
    messages = [
        {
            "role": "system",
            "content": "Reply with JSON only. Keys: title (string), priority (integer 1 to 5), tags (list of strings).",
        },
        {"role": "user", "content": text},
    ]
    for _ in range(max_tries):
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0,
        )
        reply = response.choices[0].message.content
        try:
            return Ticket.model_validate_json(reply)
        except ValidationError as error:
            messages = messages + [
                {"role": "assistant", "content": reply},
                {"role": "user", "content": f"Your reply was invalid: {error}\nFix it and reply with JSON only."},
            ]
    raise ValueError("could not get a valid ticket")
