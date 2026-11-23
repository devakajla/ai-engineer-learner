# GenAI: calling Groq

Plain-English look-up for the Groq SDK (`pip install groq`, or `uv add groq`). The API copies the OpenAI shape.

| Tool | Does |
| --- | --- |
| `Groq(api_key=..., timeout=...)` | make the client (reads `GROQ_API_KEY` if no key is given) |
| `client.chat.completions.create(...)` | one model call |
| `response.choices[0].message.content` | the answer text |
| `response.choices[0].finish_reason` | `"stop"` (done) or `"length"` (cut off) |
| `response.usage.prompt_tokens / completion_tokens / total_tokens` | token counts |
| `stream=True` | get chunks instead of one response |
| `chunk.choices[0].delta.content` | one piece of text (can be `None`) |

## The call
```python
import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])
response = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[{"role": "user", "content": "Say hi"}],
)
print(response.choices[0].message.content)   # -> Hi there!
```
**Gotcha:** the text is not in `response.text`. Go `choices[0].message.content`. Check model names at `console.groq.com/docs/models`, they change.

## Messages and roles
```python
messages = [
    {"role": "system", "content": "Be brief."},   # rules, first
    {"role": "user", "content": "What is a list?"},
    {"role": "assistant", "content": "An ordered collection."},
    {"role": "user", "content": "Example?"},
]
```
**Gotcha:** the model has no memory. Send the whole history each call. History grows, so input tokens and cost grow too.

## Settings
| Name | Meaning |
| --- | --- |
| `temperature` | 0 to 2. Low is steady, high is varied |
| `max_completion_tokens` | most tokens in the answer (old name `max_tokens`, deprecated) |
| `top_p` | other way to limit choices. Change this or temperature, not both |
| `stop` | text (or list) where the answer ends |
| `top_k` | keep only the k most likely words (not offered by Groq's chat API at time of writing; check the docs) |
| `seed` | best-effort repeatable answers |
| `reasoning_format` | for thinking models: `raw` (thinking inside content in think tags), `parsed` (separate field), `hidden` (removed). Support differs by model, check the docs |

```python
params = {"temperature": 0, "max_completion_tokens": 200}
client.chat.completions.create(model=m, messages=msgs, **params)   # ** spreads the dict
```
**Gotcha:** a cut-off answer is not an error. Check `finish_reason == "length"`.

## Streaming
```python
stream = client.chat.completions.create(model=m, messages=msgs, stream=True)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```
**Gotcha:** some chunks have no text, or no `choices`. Check before you use them.

## Errors
| Exception | Cause | Retry? |
| --- | --- | --- |
| `BadRequestError` (400) | bad parameter, input too long | no |
| `AuthenticationError` (401) | bad key | no |
| `NotFoundError` (404) | model name wrong | no |
| `RateLimitError` (429) | too many requests | yes, after a wait |
| `InternalServerError` (5xx) | server problem | yes |
| `APIConnectionError`, `APITimeoutError` | network or too slow | yes |

```python
delays = [min(1 * 2**i, 30) for i in range(4)]   # -> [1, 2, 4, 8]
```
**Gotcha:** the SDK already retries twice (`max_retries=2`). Set your own `timeout` and retry rules in production.

## Tokens and cost
```python
tokens = (len(text) + 3) // 4                  # rough: 4 characters per token, rounded up
cost = tokens / 1_000_000 * price_per_million  # input and output have different prices
```
**Gotcha:** context window = input tokens + output tokens.

## Prompt patterns
```python
messages = [
    {"role": "system", "content": "Label the sentiment."},
    {"role": "user", "content": "I love it"},        # example input
    {"role": "assistant", "content": "positive"},    # example output (few-shot)
    {"role": "user", "content": "So bad"},           # the real question
]
prompt = "Answer only from the text.\n\n<document>\n" + text + "\n</document>"   # delimiters
```
**Gotcha:** never trust the reply format. Clean it (`strip().lower().strip(".")`) and check it against the allowed values.

## Templates
```python
template = "Translate to {language}:\n{text}"
template.format(**{"language": "Hindi", "text": "Hello"})   # -> 'Translate to Hindi:\nHello'
'JSON like {{"a": 1}}'.format()                              # -> 'JSON like {"a": 1}'
from string import Formatter
[n for _, n, _, _ in Formatter().parse("{a} {b}") if n]      # -> ['a', 'b']
```
**Gotcha:** a missing value raises `KeyError`. A real brace must be doubled: `{{` and `}}`. Compare versions as numbers (`int("v10"[1:])`), not as text.

## JSON
```python
import json
json.loads('{"a": true}')                  # -> {'a': True}
json.dumps({"a": True})                    # -> '{"a": true}'
client.chat.completions.create(model=m, messages=msgs, response_format={"type": "json_object"})
```
**Gotcha:** JSON mode needs the word "JSON" in the messages. It guarantees valid syntax, not the right keys or types. Bad text raises `json.JSONDecodeError`.

## Pydantic checks
```python
from pydantic import BaseModel, Field, ValidationError

class Ticket(BaseModel):
    title: str = Field(min_length=1)
    priority: int = Field(ge=1, le=5)
    tags: list[str] = []

Ticket.model_validate_json('{"title": "a", "priority": "2"}')   # -> Ticket(title='a', priority=2, tags=[])
Ticket.model_json_schema()                                       # the schema, for your prompt
```
**Gotcha:** `"2"` is converted to `2` by default. Bad JSON text is also a `ValidationError`. Repair loop: add the bad reply and the error message to the messages, then retry a few times.

## Tool calling
```python
tools = [{"type": "function", "function": {"name": "get_weather", "description": "...",
          "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}}]
response = client.chat.completions.create(model=m, messages=msgs, tools=tools)
message = response.choices[0].message
for call in message.tool_calls or []:
    args = json.loads(call.function.arguments)                       # a JSON string
    result_message = {"role": "tool", "tool_call_id": call.id, "content": str(run(call.function.name, args))}
```
**Gotcha:** the model never runs the function, your code does. Send back the assistant message (with its `tool_calls`) and then the `tool` messages. `tool_calls` is `None` when there is no call. Return error text for unknown tools or bad arguments.

## Chat memory
```python
history[-n:]                 # last n messages. n = 0 gives EVERYTHING (the -0 trap)
cut = len(history) - keep    # safe split into old and recent
old, recent = history[:cut], history[cut:]
for m in reversed(history): ...   # newest first. list.reverse() returns None
```
**Gotcha:** trim what you send, not what you store. Do not call the model for a summary when the history is already short.

## Agent loop (level 5)
```python
for step in range(max_steps):
    message = client.chat.completions.create(model=m, messages=messages, tools=tools).choices[0].message
    if not message.tool_calls:
        return message.content                                   # done
    messages.append(message_to_dict(message))                   # the assistant message WITH its tool_calls
    for call in message.tool_calls:
        messages.append({"role": "tool", "tool_call_id": call.id, "content": run_tool_call(call, functions)})
# out of steps: stop with a clear reason ("max_steps"), never loop forever
```
**Gotcha:** every step resends the whole history, so cost grows faster than the step count. Stop reasons: `done`, `max_steps`, `loop` (the same name and arguments asked again and again). Tool errors go back to the model as text.

## Streaming to a browser (SSE)
```python
def format_sse(data, event=None):
    head = f"event: {event}\n" if event else ""
    return head + "".join(f"data: {line}\n" for line in data.split("\n")) + "\n"   # a blank line ends the event

StreamingResponse(generator(), media_type="text/event-stream",
                  headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```
**Gotcha:** the status `200` is sent with the first byte, so a failure in the middle travels as an `error` event and no `done` follows. A proxy that buffers makes the stream arrive all at once.

## Cache, rate limit, cost
```python
key = hashlib.sha256(json.dumps({"m": model, "msgs": messages, "t": temperature}, sort_keys=True).encode()).hexdigest()
recent = [t for t in timestamps if now - t < window]          # sliding window
allowed = len(recent) < limit
cost = in_tokens / 1_000_000 * in_price + out_tokens / 1_000_000 * out_price
p95 = sorted(times)[math.ceil(0.95 * len(times)) - 1]
```
**Gotcha:** cache only at `temperature=0`, and never share private answers between users. `sort_keys=True` makes the same data give the same key. Report p95, not only the average.

## Guardrails (level 5)
```python
if not text.strip() or len(text) > max_chars: ...             # input checks first, no model call
core = word.rstrip(".,;:!?"); tail = word[len(core):]          # keep the punctuation when you mask a word
if name not in allowed: refuse                                 # allow-list for tools
if name in risky and not approve(name, args): refuse           # human approval for risky actions
```
**Gotcha:** a prompt rule is a request, not a lock. Put limits in code: allow-lists, validated arguments, ownership checks, approval for irreversible actions. Injection has no full fix, so limit the damage a success can do.

## Agentic patterns (agentic track, level A1)
```python
reliability = step_success ** steps                    # 0.95 ** 10 -> 0.5987: errors multiply
current = step.replace("{input}", current)             # prompt chain: output of one step feeds the next
label = reply.lower().strip(".");  label = label if label in routes else "other"   # router: clean, then default
steps = [line.split(". ", 1)[1] for line in text.splitlines() if line[:1].isdigit()]  # plan text -> list (check the format!)
if used.get("steps", 0) >= limits["max_steps"]: stop   # budget: check before EVERY step
```
**Gotcha:** an agent is slower, costlier and less predictable than a workflow, so start with one call and climb only when a test shows the need. Tool results go into the history on every later step, so truncate them. Never trust the model's format: clean, validate, and keep a default. Every loop (improve, plan, agent) needs a hard limit.
