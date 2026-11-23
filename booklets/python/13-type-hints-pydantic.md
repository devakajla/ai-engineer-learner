# 13. Type hints and Pydantic

Python does not force you to declare types. That is quick to write, but in big programs you forget what each function expects. **Type hints** are notes in the code that say "this should be an `int`". Python itself does not enforce them, but editors, checkers (like `mypy`) and libraries such as **FastAPI and Pydantic** use them heavily. For an AI engineer, this chapter is the bridge into FastAPI.

## Writing hints

```python
def greet(name: str, times: int = 1) -> str:
    return name * times

print(greet("a", 2))
# -> aa
print(greet.__annotations__)
# -> {'name': <class 'str'>, 'times': <class 'int'>, 'return': <class 'str'>}
```

After a colon you write the type of a parameter. After `->` you write the return type. Python only **stores** them. Calling `greet(5)` is not stopped. The value is in tools and readers: your editor warns you, and a reader knows the contract at a glance.

## Common shapes

| You want to say | Write |
| --- | --- |
| a list of ints | `list[int]` |
| a dict of str to int | `dict[str, int]` |
| a tuple of fixed shape | `tuple[int, str]` |
| exact allowed values | `Literal["asc", "desc"]` |
| any function | `Callable[[int], str]` |
| anything | `Any` |

Two more shapes use the pipe sign, which does not fit in a table cell:

```python
x: int | None      # an int, or nothing
y: int | str       # one of several types
```

`int | None` (Python 3.10 and newer) replaced the old `Optional[int]`. It means "an int, or `None`". Note that it does **not** make the argument optional to pass. A default value does that.

## Why bother?

1. **Fewer bugs.** `mypy` or your editor finds a wrong call before you run the code.
2. **Documentation that cannot go out of date** the way comments do.
3. **Frameworks read them.** FastAPI looks at your hints to know whether `item_id: int` comes from the URL and must be a number. That is the whole trick behind its automatic validation.

## The limit of plain hints: no checking

```python
def double(n: int) -> int:
    return n * 2

print(double("ab"))
# -> abab
```

No error. Hints are not rules at run time. For real checking of data that comes from **outside** your program (user input, JSON, an API), you need a library that enforces them. The standard answer is **Pydantic**.

## Pydantic: types that are enforced

Install: `uv add pydantic`. A model is a class whose fields are annotated. Pydantic **checks and converts** data when you create the object.

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
    email: str | None = None

u = User(name="A", age="30")
print(u)
# -> name='A' age=30 email=None
print(type(u.age))
# -> <class 'int'>
```

The text `"30"` was converted to the number `30`, because it was clearly a number. (This friendly converting is called **coercion**.) `Field(ge=0, le=150)` adds rules: "greater or equal 0, less or equal 150". Read `BaseModel`: every model inherits from it, so it brings checking and the helpers below. (For now, copy this shape. Chapter 9 explained classes.)

### What a failure looks like

```python
from pydantic import ValidationError

try:
    User(name="A", age=-1)
except ValidationError as error:
    print(error.errors()[0]["loc"], error.errors()[0]["msg"])
# -> ('age',) Input should be greater than or equal to 0
```

The error says **which field** (`loc`) and **why** (`msg`). This is exactly the information that FastAPI sends back in a `422` response.

### Converting in and out

```python
u = User.model_validate({"name": "B", "age": 5})
print(u.model_dump())
# -> {'name': 'B', 'age': 5, 'email': None}
print(u.model_dump_json())
# -> {"name":"B","age":5,"email":null}
print(User.model_validate_json('{"name":"C","age":6}'))
# -> name='C' age=6 email=None
```

`model_validate` builds a model from a dict, `model_dump` turns it back into a dict, and the `_json` versions work with JSON text. This is the daily use: parse the JSON that an API or an LLM gives you, and get a checked object or a clear error.

### Custom checks and cleanup

```python
from pydantic import field_validator

class Signup(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def clean(cls, value):
        return value.strip().title()

print(Signup(name="  asha  ").name)
# -> Asha
```

The decorator marks a function that runs on that field. It can clean the value and return it, or raise `ValueError` to reject it.

## Pydantic for AI work

Language models often return JSON as text. You cannot trust it to be correct, so you validate it with a Pydantic model. If it fails, you can tell the model what was wrong and ask again. The GenAI booklet uses this pattern a lot.

::: {.box .checkpoint}
**Checkpoint:** you can explain why Python does not enforce hints, what Pydantic adds, and what `loc` and `msg` in a validation error tell you.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Believing type hints are checked when the program runs.
- Using `Optional[int]` and thinking the parameter becomes optional to pass. It only allows `None`.
- Mutable default values in Pydantic fields. Use `Field(default_factory=list)`.
- Trusting JSON from outside without a model.
- Forgetting that Pydantic converts `"30"` to `30` (coercion), which may or may not be what you want.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Does Python check type hints?** No. Only external tools and libraries use them.

**Q: Why does FastAPI need type hints?** It reads them to decide where data comes from, to validate it, and to build the API docs.

**Q: Pydantic vs a dataclass?** Both describe fields. Pydantic also validates and converts data. A dataclass does not check types.

**Q: `Optional[int]` vs `int | None`?** They mean the same thing. The second is the modern style.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Add type hints to three of your earlier functions.
2. Write a `Product` model with `name` (not empty), `price` (more than 0) and `tags` (a list, default empty).
3. Feed it the dict `{"name": "pen", "price": "12.5"}` and look at the types.
4. Feed it bad data and print each error's `loc` and `msg`.
5. Add a validator that lower-cases every tag.
6. **Think:** why is validating the JSON from a language model a good idea?
:::
