# Allocate books (split array largest sum)

`pages[i]` is the number of pages of book `i`. Give the books, **in order and in contiguous groups**, to `students` students (every student gets at least one book, `students <= len(pages)`). Write `allocate_books(pages, students)` that returns the **smallest possible value of the biggest total** any student has to read.

```python
allocate_books([12, 34, 67, 90], 2)    # -> 113    ([12, 34, 67] and [90])
allocate_books([10, 20, 30], 3)        # -> 30
```

**Think first:** pick a limit `m` for the most pages one student may read. Can you greedily check how many students you need? What are the smallest and biggest possible `m`?

**Hint:** pattern *binary search on the answer*: `lo = max(pages)`, `hi = sum(pages)`. `needed(m)`: fill a student until the next book would pass `m`, then start a new one. If `needed(m) <= students` the limit works: try smaller.
