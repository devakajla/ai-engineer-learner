# Read a plan from the model

In **plan-and-execute**, the model first writes a plan as a numbered list. Your code must turn that text into a Python list of steps. Models write numbers in two styles, `1.` and `1)`, and add other text around the list. Write `parse_plan(text)`.

- Go through the text line by line. Remove spaces at both ends of each line.
- A **step line** starts with one or more digits, then `.` or `)`, then the step text. Keep the step text, stripped.
- Skip every other line (titles, notes, empty lines). Skip a step line whose text is empty.
- Return the step texts as a list, in order. The numbers themselves are ignored (`3.` may come first).

```python
parse_plan("Plan:
1. Find the file
2) Read it
Good luck!")
# -> ['Find the file', 'Read it']
parse_plan("no steps here")
# -> []
```

**Think first:** why not just trust `text.split("
")`? What does the model add around the list that you must ignore?

**Hint:** `line[i].isdigit()` tests one character. Count the digits at the start with a `while` loop, then look at the character after them. No `import re` is needed.
