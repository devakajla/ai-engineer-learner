# 9. Classes and objects (OOP)

So far you used **built-in** types: `int`, `str`, `list`. With **classes** you create your *own* types. This is **object-oriented programming** (OOP). It matters because bigger programs (and every framework, like FastAPI) are organised around objects that hold data and the actions on that data.

## The idea: a blueprint and the things built from it

A **class** is a blueprint, like the plan of a house. An **object** (also called an **instance**) is one real house built from the plan. One plan, many houses. Each house has its own paint colour, but they all share the same structure.

@@ flow | Figure 9.1: one class, many objects.
class Dog|the blueprint;name, speak()|blue -> Dog("Rex")|object 1;name = Rex|green -> Dog("Bo")|object 2;name = Bo|green
@@ end

```python
class Dog:
    species = "canine"

    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name} says woof"

d = Dog("Rex")
print(d.speak())
# -> Rex says woof
print(d.species, Dog.species)
# -> canine canine
```

Let us read the class piece by piece, because three new things appear:

- `class Dog:` begins the blueprint.
- `__init__` is the **constructor**: it runs automatically when you create an object. Its job is to set up the object's starting data.
- `self` is the object itself. Inside a method, `self.name = name` means "store this value on **this** object". Every method takes `self` as its first parameter. Python passes it for you when you call `d.speak()`.
- Values stored on `self` (like `name`) are **attributes**: the data of the object. Functions inside a class are **methods**: the actions.
- `species` is a **class attribute**: shared by all objects, since it lives on the blueprint.

`Dog("Rex")` calls `__init__` with `name="Rex"` and returns a new object.

## Inheritance: "is a kind of"

When one class is a more specific version of another, it can **inherit**: get everything from the parent, and then add or change things.

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError

class Cat(Animal):
    def speak(self):
        return f"{self.name} meows"

print(Cat("Tom").speak())
# -> Tom meows
print(isinstance(Cat("Tom"), Animal), issubclass(Cat, Animal))
# -> True True
```

`Cat(Animal)` means "Cat is a kind of Animal". It got `__init__` for free, and **overrides** `speak` with its own version. `isinstance(x, Class)` asks "is this object a kind of that class?".

To extend a parent's method instead of replacing it, call `super()`:

```python
class Puppy(Dog):
    def __init__(self, name, age):
        super().__init__(name)
        self.age = age

    def speak(self):
        return super().speak() + "!"

print(Puppy("Bo", 1).speak())
# -> Bo says woof!
```

`super()` means "the parent class". Here it reuses the parent's setup and adds `age`.

## Dataclasses: classes for plain data

Many classes only hold data. Writing `__init__`, `__repr__` and `__eq__` by hand is boring. A **dataclass** writes them for you from a list of fields with types.

```python
from dataclasses import dataclass, field

@dataclass
class Task:
    title: str
    done: bool = False
    tags: list = field(default_factory=list)

t = Task("write")
print(t, t == Task("write"))
# -> Task(title='write', done=False, tags=[]) True
```

You get a readable display and value-based equality for free. Remember the mutable default trap from chapter 5: for a list field you must write `field(default_factory=list)`, which makes a fresh list per object. `@dataclass(frozen=True)` makes the object immutable, so changing a field raises `FrozenInstanceError`.

## Abstract classes: a contract

Sometimes a parent class should not be used directly. It only says "every child **must** provide these methods". That is an **abstract base class** (ABC).

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self): ...

class Square(Shape):
    def __init__(self, side):
        self.side = side
    def area(self):
        return self.side ** 2

print(Square(3).area())
# -> 9
Shape()
# -> TypeError: Can't instantiate abstract class Shape without an implementation for abstract method 'area'
```

Python refuses to build an incomplete class, so a forgotten method is caught at once, not later. The `@something` line above a function is a **decorator**; chapter 11 explains them.

## Properties, class methods, static methods

A **property** looks like a plain attribute, but runs code. Use it for computed values or validation:

```python
class Temp:
    def __init__(self):
        self._c = 0

    @property
    def fahrenheit(self):
        return self._c * 9 / 5 + 32

    @property
    def celsius(self):
        return self._c

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("too cold")
        self._c = value

t = Temp()
t.celsius = 100
print(t.fahrenheit)
# -> 212.0
```

The leading underscore in `_c` is a convention: "internal, please do not touch". Two more method kinds: a `@staticmethod` is a plain function placed inside a class for tidiness (no `self`), and a `@classmethod` receives the class (`cls`) instead of an object, often used as an alternative constructor.

## Composition vs inheritance

Inheritance says "is a". **Composition** says "has a": an object holds other objects. Beginners overuse inheritance. A good rule: **prefer composition**. It is more flexible and easier to change.

```python
class Engine:
    def start(self):
        return "vroom"

class Car:
    def __init__(self):
        self.engine = Engine()    # a Car HAS an Engine

    def start(self):
        return self.engine.start()
```

A Car is not a kind of Engine, so inheritance would be wrong. In FastAPI the service **has a** repository: that is composition.

## SOLID in plain words

Five design guidelines from the OOP world. Know the idea of each, since interviews ask:

| Letter | Name | Plain meaning |
| --- | --- | --- |
| **S** | Single responsibility | a class has one reason to change |
| **O** | Open/closed | add new behaviour by adding code, not editing old code |
| **L** | Liskov substitution | a child must work wherever its parent is expected |
| **I** | Interface segregation | many small contracts beat one huge one |
| **D** | Dependency inversion | depend on a contract, and pass the real thing in |

The last one is exactly what FastAPI's `Depends` does: the route asks for what it needs, and it is injected.

::: {.box .checkpoint}
**Checkpoint:** you can explain `self`, class vs object, `super()`, and why a Car should **have** an Engine, not inherit from it.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Forgetting `self` as the first parameter, or forgetting `self.` before an attribute.
- Putting a list or dict as a class attribute and sharing it by accident.
- Deep inheritance chains. Prefer small classes that hold each other.
- A class that is only a bag of functions. Use plain functions or a module instead.
- Forgetting `super().__init__(...)` in a child that defines its own `__init__`.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Class vs object?** A class is the blueprint. An object is an instance made from it.

**Q: What is `self`?** The current object, passed automatically as the first parameter of methods.

**Q: Composition vs inheritance?** Inheritance is "is a", composition is "has a". Prefer composition for flexibility.

**Q: What does `@dataclass` do?** It generates `__init__`, `__repr__` and `__eq__` from the annotated fields.

**Q: What is an abstract class?** One that cannot be instantiated and forces children to implement certain methods.

**Q: What is method overriding?** A child gives its own version of a parent's method.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Make a `BankAccount` with `deposit` and `withdraw`. Raise `ValueError` if you withdraw more than the balance.
2. Make `Circle` and `Rectangle` that both inherit from an abstract `Shape` with `area()`.
3. Turn a tuple-like record (name, age, city) into a dataclass, and print it.
4. Write a class `Temperature` with a property that refuses values below absolute zero.
5. Rewrite "a `Library` inherits from `list`" using composition.
6. **Think:** which SOLID letter is broken by a class that sends emails, saves to the database and prints reports?
:::
