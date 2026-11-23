# 18. Interview question bank

Short answers you can say aloud. Cover the answer, say yours first, then compare. The number in brackets is the chapter to re-read.

## Basics

**1. Is Python compiled or interpreted?** Both, in a way. Source is compiled to bytecode, and the interpreter (a virtual machine) runs the bytecode. [1]

**2. What is dynamic typing?** Names have no fixed type. The type belongs to the value, and is found at run time. [2]

**3. What does `//` do and how is it different from `/`?** `//` divides and rounds down. `/` always gives a float. [2]

**4. Why is `0.1 + 0.2 != 0.3`?** Floats are stored in binary, which cannot represent 0.1 exactly. Compare with a tolerance or use `Decimal`. [2]

**5. What is truthy and falsy?** Empty or zero values count as false: `0`, `""`, `[]`, `{}`, `None`. Everything else is true. [2, 3]

**6. `==` vs `is`?** Equality of value versus identity of object. Use `is` for `None`. [3]

**7. What does `a or b` return?** `a` if it is truthy, otherwise `b`. It returns one of the operands, not always a bool. [3]

## Data structures

**8. List vs tuple?** Mutable versus immutable. A tuple can be a dict key. [4]

**9. How do you remove duplicates and keep order?** `list(dict.fromkeys(items))`. [4]

**10. Why is membership in a set fast?** Hashing: it jumps straight to the item instead of scanning. [4, 17]

**11. What can be a dict key?** Any hashable (immutable) object. [4, 8]

**12. `sort()` vs `sorted()`?** In place and returns `None`, versus a new list from any iterable. [4, 7]

**13. How would you count word frequencies?** A counter dict, or `collections.Counter`. [4]

## Functions

**14. What is the mutable default argument bug?** A default like `[]` is created once at definition and shared across calls. Use `None`. [5]

**15. What are `*args` and `**kwargs`?** Extra positional arguments as a tuple, extra keyword arguments as a dict. [5]

**16. What does a function return without `return`?** `None`. [5]

**17. What is LEGB?** Name lookup order: Local, Enclosing, Global, Built-in. [11]

**18. What is a lambda?** A small anonymous one-expression function. [5]

## Data model

**19. Mutable vs immutable?** Can the object change in place. List, dict, set yes. int, str, tuple no. [8]

**20. Shallow vs deep copy?** Shallow copies the outer container only. Deep copies everything inside. [8]

**21. Is Python pass by value or by reference?** Neither. It passes a reference to the object. Mutating shows in the caller, rebinding does not. [8]

**22. `__str__` vs `__repr__`?** Friendly text for users versus precise text for developers. [8]

**23. What is a dunder method?** A special method like `__len__` or `__add__` that Python calls for built-in operations. [8]

## OOP

**24. Class vs object?** Blueprint versus instance. [9]

**25. What is `self`?** The current instance, the first parameter of methods. [9]

**26. Composition vs inheritance?** "Has a" versus "is a". Prefer composition. [9]

**27. What does `@dataclass` give you?** `__init__`, `__repr__`, `__eq__` generated from annotated fields. [9]

**28. What is an abstract class?** A class that cannot be created and forces children to implement some methods. [9]

**29. Name the SOLID principles.** Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion. [9]

## Iterators, generators, decorators

**30. What does `yield` do?** Produces a value and pauses the function, keeping its state. [10]

**31. Generator vs list?** Lazy and low memory versus all in memory now. A generator can be used once. [7, 10]

**32. What is a closure?** An inner function that remembers variables from its enclosing function. [11]

**33. What is a decorator?** A function that wraps another function. `@d` above `def f` equals `f = d(f)`. [11]

**34. Why `functools.wraps`?** To keep the original name and docstring. [11]

**35. What is `lru_cache`?** A decorator that caches results by arguments (memoization). [11]

**36. What is a context manager?** An object with `__enter__` and `__exit__` giving guaranteed setup and cleanup. [12]

## Types and Pydantic

**37. Does Python enforce type hints?** No. Tools and libraries use them. [13]

**38. What does Pydantic add?** Validation and conversion of data at run time from type hints. [13]

**39. `int | None` vs `Optional[int]`?** The same meaning. The first is the modern style. [13]

## Concurrency and performance

**40. What is the GIL?** A CPython lock letting one thread run Python bytecode at a time. [14]

**41. Threads, processes or asyncio?** Threads for blocking I/O, processes for CPU work, asyncio for many concurrent I/O tasks. [14, 15]

**42. What does `await` do?** Pauses the coroutine and lets the event loop run others until the result is ready. [15]

**43. What happens if you call `time.sleep` in an `async def`?** It blocks the loop and freezes every task. [15]

**44. `gather` vs `create_task`?** Collect many results together, versus start one in the background. [15]

**45. How do you limit concurrent tasks?** `asyncio.Semaphore`. [15]

**46. How do you find a performance problem?** Profile with `cProfile`, fix the biggest cost, measure again. [17]

**47. What is the N+1 problem?** One query for a list plus one per item. Use a join or batch load. [17]

## Testing and tools

**48. What is a fixture?** Reusable test setup injected by parameter name. [16]

**49. What is mocking?** Replacing a real dependency with a fake. [16]

**50. `pyproject.toml` vs `uv.lock`?** What you want versus the exact versions installed. [16]

## Coding drills (write them on paper, then check)

1. Reverse a string without `[::-1]`.
2. Return the most frequent character in a string.
3. Check whether two words are anagrams.
4. Flatten a nested list one level deep.
5. Write a decorator that times a function.
6. Write a generator for the Fibonacci numbers.
7. Write an `async` function that fetches three URLs together with a timeout.
8. Write a context manager that prints how long its block took.

*Sample answers to drills 1 to 3 are in the answers chapter.*
