# 4. Lists, tuples, sets and dictionaries

One variable holds one value. But real data comes in groups: a list of prices, a set of unique tags, a record with a name and an age. Python has four built-in **containers** for this. Choosing the right one is a core skill, and a favourite interview topic.

@@ grid 4 | Figure 4.1: the four containers at a glance.
list|ordered;changeable;duplicates ok;[1, 2, 2]|blue
tuple|ordered;fixed;duplicates ok;(1, 2, 2)|green
set|no order;changeable;unique only;{1, 2}|yellow
dict|key to value;changeable;unique keys;{"a": 1}|purple
@@ end

## Lists

A **list** is an ordered row of items, like a shopping list. You can add, remove and change items. Items are numbered from 0, just like string positions.

```python
nums = [3, 1, 2]
nums.append(4)
print(nums)
# -> [3, 1, 2, 4]
nums.insert(0, 9)
print(nums)
# -> [9, 3, 1, 2, 4]
```

`append` adds at the end. `insert(position, item)` adds at a position and pushes the rest along. Both **change the list itself**. This is the key difference from strings: lists are **mutable** (changeable).

Taking items out:

```python
nums = [9, 3, 1, 2, 4]
print(nums.pop())
# -> 4
print(nums.pop(0))
# -> 9
nums.remove(1)
print(nums)
# -> [3, 2]
```

`pop()` removes and **returns** the last item (or the one at a given position). `remove(value)` removes the first item *equal to* the value and returns nothing. Removing a value that is not there raises `ValueError`.

Indexing and slicing work exactly as for strings:

```python
nums = [10, 20, 30, 40]
print(nums[0], nums[-1], nums[1:3], nums[::-1])
# -> 10 40 [20, 30] [40, 30, 20, 10]
print(len(nums), 30 in nums, nums.index(30), nums.count(10))
# -> 4 True 2 1
```

### Sorting: `sort()` vs `sorted()`

```python
nums = [3, 1, 2]
print(sorted(nums), nums)
# -> [1, 2, 3] [3, 1, 2]
nums.sort()
print(nums)
# -> [1, 2, 3]
```

`sorted(x)` returns a **new** sorted list and leaves `x` alone. `x.sort()` sorts `x` **in place** and returns `None`. A classic bug is writing `nums = nums.sort()`, which leaves you with `None`. Rule of thumb: **methods that change a list in place return `None`**.

## Tuples

A **tuple** is like a list that cannot be changed after creation. Use it for a fixed group, such as a point `(x, y)` or a pair `(name, age)`.

```python
point = (3, 4)
x, y = point
print(x, y)
# -> 3 4
single = (5,)
print(type(single), type((5)))
# -> <class 'tuple'> <class 'int'>
```

The first part is **unpacking**: pull a tuple apart into separate names, in one line. The second shows a trap: a tuple with one item needs a **trailing comma**. `(5)` is just the number 5 in brackets.

Why use a tuple when a list could do? It tells the reader "this will not change", it is slightly faster, and (unlike lists) it can be a dictionary key. Functions that return several values actually return a tuple (chapter 5).

## Sets

A **set** is a bag of **unique** items with **no order**, like a drawer of distinct coins. Two superpowers: it removes duplicates, and checking "is this in the set?" is very fast, even for a million items. (A list has to look at items one by one.)

```python
s = {1, 2, 2, 3}
print(s)
# -> {1, 2, 3}
s.add(9)
print(len(s), 2 in s)
# -> 4 True
```

Sets also do school-maths set operations:

```python
a = {1, 2}
b = {2, 3}
print(a | b, a & b, a - b, a ^ b)
# -> {1, 2, 3} {2} {1} {1, 3}
```

In words: `|` union (everything), `&` intersection (in both), `-` difference (in `a` but not `b`), `^` in one but not both. Note: `{}` on its own is an empty **dict**, not an empty set. Make an empty set with `set()`.

To remove duplicates from a list but **keep order**, use a dict trick:

```python
print(list(set([3, 1, 3, 2])))
# -> [1, 2, 3]   (order is not promised)
print(list(dict.fromkeys([3, 1, 3, 2])))
# -> [3, 1, 2]
```

## Dictionaries

A **dict** stores **pairs**: a *key* and its *value*. Think of a real dictionary (word, meaning) or a phone book (name, number). You look things up by **key**, not by position. This is the most used structure in Python, and JSON data looks exactly like it.

```python
user = {"name": "Asha", "age": 26}
user["city"] = "Pune"
print(user)
# -> {'name': 'Asha', 'age': 26, 'city': 'Pune'}
print(user["name"])
# -> Asha
```

Reading a missing key with `[ ]` raises `KeyError`. When a key may be missing, use `get`, which returns `None` or a default you choose:

```python
print(user.get("zip"), user.get("zip", "unknown"))
# -> None unknown
```

Looping and the other useful methods:

```python
for key, value in user.items():
    print(key, value)
# -> name Asha
# -> age 26
# -> city Pune
print(list(user.keys()), list(user.values()))
# -> ['name', 'age', 'city'] ['Asha', 26, 'Pune']
user.update({"age": 27})
print(user.pop("city"), user)
# -> Pune {'name': 'Asha', 'age': 27}
```

`items()` gives (key, value) pairs, `keys()` and `values()` give the parts, `update` merges another dict in, and `pop(key)` removes and returns. Python dicts remember **insertion order**. Keys must be **unchangeable** types (strings, numbers, tuples), never a list.

### Pattern: the counter dict

Counting how often things appear is a daily task. Use `get` with a default of 0:

```python
counts = {}
for word in "a b a c a b".split():
    counts[word] = counts.get(word, 0) + 1
print(counts)
# -> {'a': 3, 'b': 2, 'c': 1}
```

Step by step: for each word, look up its count (0 if unseen), add 1, and store it back. After the loop, `counts` has the answer. You will meet this again as `collections.Counter`.

## Choosing the right container

| You need... | Use |
| --- | --- |
| an ordered group you will change | list |
| a fixed group, or a dict key | tuple |
| uniqueness or fast "is it in?" | set |
| to look things up by a name | dict |

::: {.box .checkpoint}
**Checkpoint:** you can say what is wrong with `nums = nums.sort()`, why `(5)` is not a tuple, why `{}` is not a set, and how to count words with a dict.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- `nums = nums.sort()` makes `nums` equal to `None`.
- Changing a list while looping over it.
- Reading a missing dict key with `[ ]` instead of `get`.
- Expecting a set to keep order, or to allow a list inside it.
- Using `{}` to create an empty set.
- Forgetting the trailing comma in a one-item tuple.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: List vs tuple?** A list is mutable and a tuple is immutable. A tuple can be a dict key and signals "fixed".

**Q: Why is `x in my_set` fast?** A set stores items by hash, so it jumps straight to the place instead of scanning.

**Q: What can be a dict key?** Any immutable (hashable) value: strings, numbers, tuples of those. Not lists or dicts.

**Q: Are dicts ordered?** Yes, in insertion order, since Python 3.7.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Make a list of five numbers. Print the largest, the smallest, the sum (`max`, `min`, `sum`) and the list reversed.
2. Remove duplicates from `[4, 1, 4, 2, 1]` while keeping the first-seen order.
3. Count the letters in `"banana"` into a dict.
4. Given `a = {1, 2, 3}` and `b = {3, 4}`, print what is only in `a`, in both, and in either.
5. Given `{"a": 1, "b": 2}`, build a new dict with keys and values swapped.
6. Find the word that appears most often in a sentence.
7. **Think:** you must store 100,000 user ids and check quickly whether an id exists. Which container, and why?
:::
