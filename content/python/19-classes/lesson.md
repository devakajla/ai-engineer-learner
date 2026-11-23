---
title: Classes & objects
summary: Create your own types with attributes and methods. Learn properties, class vs instance data, and the basics of inheritance.
plan_ids: [PY-06]
---

A **class** is a blueprint. It groups data (**attributes**) together with the functions that work on that data (**methods**). An **object** (or **instance**) is one thing made from the blueprint. Real programs, including FastAPI apps, use classes a lot: data models, services, and errors. This lesson shows you how to write them.

## Your first class

```python
class Task:
    def __init__(self, title, priority="medium"):
        self.title = title            # instance attributes
        self.priority = priority
        self.done = False

    def complete(self):               # a method
        self.done = True

t = Task("Write tests")
t.complete()
print(t.done)       # -> True
print(t.title)      # -> Write tests
```

What each part does:

- `class Task:` starts the blueprint.
- `__init__` runs when you create an object, and sets up its starting data. (Strictly, `__new__` makes the object and `__init__` fills it in.)
- `self` is the object itself. Every method takes `self` as its first parameter. You do not pass it. Python does.
- `t.complete()` is the same as `Task.complete(t)`.
- You create attributes by assigning to `self.something`.

Each object has its own attributes:

```python
a = Task("A")
b = Task("B")
a.complete()
print(a.done, b.done)    # -> True False
```

## Class data and instance data

An **instance attribute** belongs to one object. A **class attribute** is written directly in the class and is **shared** by all objects.

A step-by-step example: give every student a number that goes up by one.

1. Keep a counter in the class: `_next_id = 1`.
2. In `__init__`, give the new student the current number.
3. Then add 1 to the counter in the class, with `Student._next_id += 1`.

```python
class Student:
    _next_id = 1                      # class attribute: one copy for all students

    def __init__(self, name):
        self.name = name              # instance attribute: one per student
        self.id = Student._next_id
        Student._next_id += 1

a = Student("Ada")
b = Student("Linus")
print(a.id, b.id)           # -> 1 2
print(Student._next_id)     # -> 3
```

Python looks for an attribute in this order: the object, then its class, then the parent classes.

Be careful: **assigning** through an object creates a new instance attribute that hides the class attribute:

```python
class Task:
    count = 0

t = Task()
t.count = 5
print(t.count)       # -> 5
print(Task.count)    # -> 0    the class attribute did not change
```

> Danger: a **mutable** class attribute (like `tags = []`) is shared by every object. This is the class version of the mutable default argument bug. Create lists and dicts in `__init__`.

```python
class Team:
    def __init__(self):
        self.members = []        # a new list for each Team

    def add(self, name):
        self.members.append(name)
```

## `@property`: attributes with rules

Sometimes an attribute needs a check, or must be worked out from other data. A **property** looks like a normal attribute from the outside, but runs code.

A read-only property has only a getter:

```python
class Account:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

acc = Account(100)
print(acc.balance)      # -> 100
acc.balance = 5         # AttributeError: can't set attribute (no setter)
```

To allow changes, add a **setter**, where you can check the value:

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius          # this goes through the setter below

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):               # computed from celsius
        return self._celsius * 9 / 5 + 32

t = Temperature(100)
print(t.fahrenheit)    # -> 212.0
t.celsius = -500       # ValueError
```

Callers use plain attribute syntax (`t.fahrenheit`), and you can add checks later **without changing how the class is used**. That is why Python does not need `get_x()` and `set_x()` methods.

A name that starts with `_` (like `_celsius`) is a **convention** that means "internal, please do not touch". Python has no real private attributes.

## `@classmethod` and `@staticmethod`

```python
class Task:
    def __init__(self, title, priority="medium"):
        self.title = title
        self.priority = priority

    @classmethod
    def from_dict(cls, data):              # another way to build a Task
        return cls(data["title"], data.get("priority", "medium"))

    @staticmethod
    def is_valid_title(title):             # a helper that needs no object
        return 0 < len(title.strip()) <= 200

t = Task.from_dict({"title": "Ship it"})
print(t.priority)                          # -> medium
print(Task.is_valid_title(""))             # -> False
```

- A **classmethod** receives the class (`cls`). It is perfect for alternative ways to build an object. It also works for subclasses.
- A **staticmethod** receives nothing. It is a plain function that lives inside the class for tidiness.

A classmethod can also read and change class attributes. This is how you can build a counter with helpers:

```python
class Visitor:
    _count = 0

    def __init__(self):
        Visitor._count += 1

    @classmethod
    def total(cls):
        return cls._count

Visitor(); Visitor()
print(Visitor.total())    # -> 2
```

## `__repr__` and `__str__`

These control how an object is shown as text.

```python
class Task:
    def __init__(self, title):
        self.title = title
        self.done = False

    def __repr__(self):
        return f"Task(title={self.title!r}, done={self.done})"

t = Task("Ship it")
print(repr(t))     # -> Task(title='Ship it', done=False)
```

- `__repr__` is the clear, exact version for developers (the REPL, logs, the debugger). **Always write one.**
- `__str__` is the friendly version for users (what `print` uses). If you do not write it, Python uses `__repr__`.
- `!r` inside an f-string means "use `repr()` of this value". For a string it adds the quotes: `'Ship it'`.

## Inheritance (the basics)

A class can **inherit** from another class. It gets all the attributes and methods of its **parent**, and can add or change them.

```python
class Notification:
    def __init__(self, to):
        self.to = to

    def send(self, message):
        raise NotImplementedError      # children must write this

class EmailNotification(Notification):
    def __init__(self, to, subject):
        super().__init__(to)           # run the parent's __init__
        self.subject = subject

    def send(self, message):           # override the parent's method
        return f"email to {self.to}: {self.subject}"

n = EmailNotification("dev@example.com", "Hi")
print(n.send("hello"))                 # -> email to dev@example.com: Hi
print(isinstance(n, Notification))     # -> True
```

- `class Child(Parent)` inherits from `Parent`.
- `super()` gives you the parent. When you write your own `__init__` in a child, call `super().__init__(...)` first.
- `isinstance(obj, Parent)` is `True` for child objects too.

The next lesson shows when **not** to use inheritance, and some handy tools like dataclasses.

## A little deeper (optional)

- A double underscore name (`__x`) is **name-mangled** to `_ClassName__x`. This avoids clashes in subclasses. It is not for security.
- Type hints like `title: str` describe what a value should be. You will learn them in lesson 27.

## Common mistakes

- Forgetting `self` as the first parameter: `TypeError: takes 0 positional arguments but 1 was given`.
- Using a mutable class attribute that all objects share.
- Not calling `super().__init__()` in a child class.
- Writing `get_x()` and `set_x()` methods when a property would do.

## Interview corner

- **Q: What is the difference between `@classmethod` and `@staticmethod`?** A classmethod gets the class and is used for alternative constructors. A staticmethod gets nothing.
- **Q: What is `self`?** The object the method was called on. `obj.m()` is the same as `Class.m(obj)`.
- **Q: How does Python look up an attribute?** In the object first, then the class, then the parent classes.
- **Q: Does Python have private attributes?** No. `_x` is a convention, and `__x` is name-mangled.

## Summary

- `__init__` sets up the instance attributes on `self`. Methods take `self` first.
- Class attributes are shared by all objects. Never make them mutable by accident.
- `@property` gives checked or computed attributes with plain syntax. No setter means read-only.
- `@classmethod` is for alternative constructors. `@staticmethod` is for helper functions.
- Always write a useful `__repr__`. Use `super()` in child classes.
