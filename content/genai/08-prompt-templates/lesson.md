---
title: Prompt templates in code
summary: Keep prompts as reusable templates with placeholders, fill them safely, check for missing values, and version them.
plan_ids: []
---

In lesson 7 you built prompts with f-strings inside functions. That works for one prompt. A real app has many prompts, and they change often. You need a clean way to **store, fill and change** them.

A **prompt template** is a prompt with holes in it, called **placeholders**. You fill the holes later with real values.

Think of a form letter: "Dear {name}, your order {order_id} has shipped." The letter is written once. You fill in the name and the number for each customer. A prompt template works the same way.

## Placeholders with `str.format`

A placeholder is a name inside curly braces. The string method `.format(...)` fills them.

```python
template = "Explain {topic} to a {level}."

print(template.format(topic="an API", level="beginner"))
# -> Explain an API to a beginner.
```

You can also give the values as a dictionary. `**values` spreads the dictionary into named arguments (you saw this in lesson 5):

```python
values = {"topic": "a token", "level": "child"}
print(template.format(**values))
# -> Explain a token to a child.
```

Why not an f-string? An f-string fills the values **right where you write it**. A template is written once, kept in one place, and filled **later**, maybe somewhere else, maybe many times.

## Missing values

If a value is missing, `.format` raises a `KeyError`:

```python
try:
    "Explain {topic}.".format()
except KeyError as e:
    print("missing:", e)   # -> missing: 'topic'
```

The message is not very friendly. Catch it and raise your own clear error.

### Step by step: a safe `render`

1. Try to fill the template with `.format(**values)`.
2. If a `KeyError` happens, the missing name is `e.args[0]`.
3. Raise a `ValueError` with a clear message.

```python
def render(template, values):
    try:
        return template.format(**values)
    except KeyError as e:
        raise ValueError(f"missing variable: {e.args[0]}")

render("Hi {name}!", {"name": "Dev"})   # -> 'Hi Dev!'
render("Hi {name}!", {})                # raises ValueError: missing variable: name
```

This is the same pattern as the first exercise: wrap one risky call, turn the error into a clearer one.

Extra values that the template does not use are fine. `.format` ignores them.

## Braces in the text

What if your prompt must contain a real `{` or `}`? For example, a JSON example. Double them: `{{` and `}}`.

```python
template = 'Reply as JSON like {{"answer": "{x}"}}'
print(template.format(x="yes"))
# -> Reply as JSON like {"answer": "yes"}
```

Forgetting this is the most common template bug.

## Finding the placeholders

Sometimes you want to know which names a template needs, for example to check the values before you fill it. Python has a tool in the `string` module:

```python
from string import Formatter

parts = list(Formatter().parse("Hi {name}, you are {age}."))
print(parts)
# -> [('Hi ', 'name', '', None), (', you are ', 'age', '', None), ('.', None, None, None)]
```

`parse` splits the template into pieces. Each piece is a tuple: the text before, then the **field name** (or `None` if there is no placeholder), and two more values you can ignore. To list the names:

1. Loop over the pieces.
2. Unpack each as `text, name, spec, conv`.
3. If `name` is not `None`, it is a placeholder. Add it.

```python
def names(template):
    found = []
    for text, name, spec, conv in Formatter().parse(template):
        if name is not None:
            found.append(name)
    return found

names("Hi {name}, you are {age}.")   # -> ['name', 'age']
names("No holes here")               # -> []
```

## Keep prompts in one place

Do not scatter prompt text through your code. Put them in one dictionary or file:

```python
PROMPTS = {
    "summary": "Summarize in one sentence:\n{text}",
    "translate": "Translate to {language}:\n{text}",
}

render(PROMPTS["translate"], {"language": "Hindi", "text": "Good morning"})
```

Now a teammate can find and improve every prompt in one file.

## Putting it together: render a stored prompt

Combine the two ideas: look up a prompt by name, then fill it. The steps:

1. Get the template text from the registry (by name, and by version if given).
2. Fill it with the values.
3. Return the finished prompt.

Here is the shape with a different example (greeting cards):

```python
CARDS = {"birthday": "Happy birthday, {name}!", "thanks": "Thank you, {name}, for {reason}."}

def make_card(kind, values):
    template = CARDS[kind]
    return template.format(**values)

make_card("thanks", {"name": "Asha", "reason": "your help"})
# -> 'Thank you, Asha, for your help.'
```

You will do the same with your own `render` and `get_prompt` functions in the fourth exercise. When you reuse two small functions to make a third, you are building a toolbox. That is how real code grows.

## Versions

Prompts change. A new version may be better, or worse. So give each prompt **versions**, so you can go back, and compare:

```python
PROMPTS = {
    "qa": {
        "v1": "Answer: {question}",
        "v2": "Answer briefly and politely: {question}",
    }
}
```

To get the latest version, find the highest number. The names are `v1`, `v2`, ... `v10`. Compare them as **numbers**, not as text. As text, `"v10"` comes before `"v2"`. Cut off the first letter with `[1:]` and use `int(...)`:

```python
names = ["v1", "v10", "v2"]
print(max(names))                       # -> v2        (wrong: text order)
print(max(int(n[1:]) for n in names))   # -> 10        (right)
```

To find the **name** that has the highest number, remember the best as you loop:

```python
best_name = None
best_number = -1
for name in names:
    number = int(name[1:])
    if number > best_number:
        best_name = name
        best_number = number
print(best_name)   # -> v10
```

Keep the version name in your logs. When an answer looks bad, you will know which prompt wrote it.

## Try it live

1. Write a template `"Explain {topic} to a {level}."`. Fill it with three different values and send each to the model. Same code, three different answers.
2. Leave one value out on purpose. Read the error. Is it clear enough to fix the bug in one minute?
3. Make a `v1` and a `v2` of the same prompt (for example, `v2` adds "Use at most 2 sentences."). Send the same question with both. Which is better? This is how prompts are improved, one small change at a time.

## A little deeper

- **Template engines.** For long prompts with loops and `if` parts, people use **Jinja2**. For most prompts, `.format` is enough. Do not add a library you do not need.
- **Injection through placeholders.** If the value comes from a user, they can write anything into the hole: "Ignore the rules above". A template does not clean values. Delimiters from lesson 7 help.
- **`format_map` and `string.Template`.** `format_map` takes a dictionary without `**`. `string.Template` uses `$name` and never breaks on braces, which is handy for text full of `{}`.
- **Prompts as files.** Large prompts live well in `.txt` or `.md` files in a `prompts/` folder, loaded when the app starts. Then changing a prompt is a small, reviewable change in git.
- **Evaluate before switching.** A new version may look better on one example and be worse on average. In Level 4 you will measure this with an eval set.
- **Frameworks** (LangChain and others) have their own template classes. They do what you just wrote, plus extras.

## Common mistakes

- Forgetting to double the braces `{{ }}` around a JSON example.
- A typo in a placeholder name, so you get `KeyError` at run time.
- Comparing version names as text (`"v10" < "v2"`).
- Editing a prompt and losing the old one. Add a new version instead.
- Filling a template with user text, and trusting it.

## Interview corner

**Why use prompt templates instead of building strings in code?**
Templates keep prompts in one place, so they are easy to review, version, test and change without touching logic.

**How do you version and test prompts?**
Store each version by name, log the version with every call, and compare versions on a fixed set of test questions before switching.

**What is a prompt injection risk with templates?**
A user-supplied value goes into the prompt and can contain instructions. Treat inputs as data: use delimiters, limit what they can do, and check the output.

**What is the problem with JSON examples inside a `.format` template?**
The braces in the JSON look like placeholders. You must double them: `{{` and `}}`.

## Summary

- A template has `{placeholders}`. Fill with `template.format(**values)`.
- A missing value raises `KeyError`. Turn it into a clear `ValueError`.
- Real braces in the text: write `{{` and `}}`.
- `string.Formatter().parse(template)` lists the placeholders.
- Keep prompts in one place, with versions (`v1`, `v2`). Compare version numbers as numbers.
- Project: step 4 adds a `prompts.py` module with a versioned question-answering prompt.
- Reference: `reference/genai-groq.md`.
