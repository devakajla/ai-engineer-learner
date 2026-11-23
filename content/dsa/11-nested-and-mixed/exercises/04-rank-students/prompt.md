# Rank students

Write `rank_students(students)` that takes a list of dicts like `{"name": "Asha", "score": 80}` and returns a list of **names**, best score first. If scores are equal, sort by name A to Z.

```python
rank_students([
    {"name": "Dev", "score": 90},
    {"name": "Asha", "score": 90},
    {"name": "Ravi", "score": 70},
])
# -> ['Asha', 'Dev', 'Ravi']
```

**Think first:** what are the two sort rules? Which one needs reversing?

**Hint:** a helper `def key(s): return (-s["score"], s["name"])` and `sorted(students, key=key)`.
