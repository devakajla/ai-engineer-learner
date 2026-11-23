# 8. The data model: names, objects and copies

This is the chapter that turns a beginner into someone who really understands Python. Many mysterious bugs (a list that changes "by itself", a function that alters your data) come from one idea you will learn here: **names point to objects**.

## Names are labels, objects are things

In chapter 2 we said a variable is a label on a value. Now we sharpen it. Python keeps **objects** (the actual values) in memory. A **name** is a label that points to an object. Several names can point to the **same** object.

```python
a = [1, 2]
b = a
b.append(3)
print(a)
# -> [1, 2, 3]
```

`b = a` did **not** copy the list. It stuck a second label on the same list. So changing it through `b` shows through `a`.

@@ grid 3 | Figure 8.1: names a and b both point to the one list in the middle.
a|a label|blue
[1, 2, 3]|ONE list object in memory|green
b|another label|blue
@@ end

You can check with `is` (chapter 3): `a is b` is `True`, meaning one object. `id(a)` shows the object's identity number.

## Mutable and immutable

- **Mutable** objects can be changed in place: list, dict, set.
- **Immutable** objects cannot: int, float, str, tuple, bool, None.

This explains why two names behave differently:

```python
x = 5
y = x
y += 1
print(x, y)
# -> 5 6
```

You cannot change the number 5, so `y += 1` makes a **new** object 6 and moves the label `y` to it. `x` still points to 5. With the list, `append` changed the *object itself*, so every name saw it.

The same explains this one:

```python
def add_one(items):
    items.append(1)

data = []
add_one(data)
print(data)
# -> [1]
```

Python passes **the label's target** to the function, so the function and the caller share the same list. A function can change a mutable argument. If you do not want that, copy it first.

## Copying

To get an independent list, make a copy.

```python
a = [1, 2]
c = a.copy()
c.append(4)
print(a, c)
# -> [1, 2] [1, 2, 4]
```

(Other ways: `list(a)` and `a[:]`.) This is called a **shallow copy**: it makes a new outer container, but the items inside are still the *same objects*. For flat lists that is fine. With **nested** data, it bites:

```python
nested = [[1], [2]]
shallow = nested.copy()
shallow[0].append(9)
print(nested)
# -> [[1, 9], [2]]
```

The outer lists are different, but the inner `[1]` is shared. For a fully independent copy, use a **deep copy**, which copies everything inside, at every level:

```python
import copy

deep = copy.deepcopy(nested)
deep[0].append(7)
print(nested, deep)
# -> [[1, 9], [2]] [[1, 9, 7], [2]]
```

Rule of thumb: flat data, `.copy()`. Nested data, `copy.deepcopy`.

## Equality and identity (recap)

`==` compares values. `is` compares identity. Two equal lists are different objects. Do not use `is` for numbers or text. (Python sometimes reuses small numbers and short strings, so `is` can look like it works and then fail. It is not reliable.)

## Hashing: why dict keys must be immutable

A dict and a set find things fast by turning a key into a number, its **hash**. If the key could change, its hash would change and the item would be lost. So only **hashable** (immutable) objects can be keys. `hash("a")` gives the same number every time within a run.

## Special methods (dunder methods)

How does `len(x)` or `a + b` work for your own types? Python calls special methods with **double underscores** on both sides, nicknamed "**dunder**" (double under). You define them in a class (chapter 9 explains classes, so just read along):

| Written by you | Python calls it when you do... |
| --- | --- |
| `__repr__` | `repr(x)`, and the display inside lists and the console |
| `__str__` | `print(x)` and `str(x)` |
| `__eq__` | `x == y` |
| `__len__` | `len(x)` |
| `__add__` | `x + y` |
| `__iter__` | `for i in x` |

```python
class P:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"P({self.name!r})"
    def __str__(self):
        return f"person {self.name}"
    def __eq__(self, other):
        return self.name == other.name

p = P("a")
print(p, repr(p), [p], p == P("a"))
# -> person a P('a') [P('a')] True
```

`__str__` is for **users** (readable), `__repr__` is for **developers** (precise, ideally something you could type to rebuild the object). Without `__eq__`, two separate `P("a")` would not be equal, because the default compares identity.

::: {.box .checkpoint}
**Checkpoint:** you can draw why `b = a` shares a list, explain shallow vs deep copy, and say why a list cannot be a dict key.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Thinking `b = a` copies a list or a dict.
- A function that changes a list given by the caller without saying so.
- Using `.copy()` on nested data and being surprised.
- Using `is` to compare values.
- Writing `[[0] * 3] * 3` for a grid: the three rows are the **same** list. Use `[[0] * 3 for _ in range(3)]`.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Mutable vs immutable?** Mutable objects can change in place (list, dict, set). Immutable ones cannot (int, str, tuple).

**Q: Shallow vs deep copy?** A shallow copy copies the outer container only, so inner objects are shared. A deep copy copies all levels.

**Q: Does Python pass by value or by reference?** Neither exactly. It passes a reference to the object ("pass by assignment"). Mutating a mutable argument shows in the caller. Re-assigning the name does not.

**Q: `__str__` vs `__repr__`?** `__str__` is the friendly text. `__repr__` is the developer-facing one, used as a fallback.

**Q: Why must dict keys be hashable?** Lookup uses the hash, so the key must not change.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Predict then test: `a = [1]; b = a; b += [2]; print(a)`.
2. Make a function `with_tax(prices)` that returns a **new** list and leaves the input unchanged.
3. Create a nested list, copy it shallow and deep, change an inner item, and print all three.
4. Build a 3x3 grid of zeros safely, and show the wrong way's bug.
5. Create a class with `__repr__` and `__eq__`, and print it inside a list.
6. **Think:** why can a tuple be a dict key, but a tuple that contains a list cannot?
:::
