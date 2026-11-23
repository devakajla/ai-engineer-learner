# Functions and problem patterns

## Function basics
- `return` hands a value back; `print` only shows text. A function without `return` gives `None`.
- First `return` reached ends the function.
- Defaults: `def power(base, exp=2)`. Keywords: `power(exp=3, base=2)`.
- Return several values as a tuple: `return a, b`.
- **Gotcha:** never use a mutable default like `items=[]`.

## The 5-step routine
1. Understand input and output. 2. Solve an example by hand. 3. Plan in plain words. 4. Code. 5. Test edges (empty, one item, repeats, negatives).

## Pattern catalog

| Pattern | Idea | Skeleton | Lesson |
| --- | --- | --- | --- |
| Accumulator | running total/product | `total = 0` then `total += x` | dsa/03 |
| Counter | count matches | `if cond: count += 1` | dsa/03 |
| Early exit | return once known | `return True` in loop, `return False` after | dsa/03 |
| Build a list | collect results | `result = []` ... `append` | dsa/03 |
| Best so far | max/min/answer | `best = items[0]` ... update | dsa/01, 07 |
| Peel digits | work on digits | `n % 10`, `n //= 10` | dsa/02 |
| Row builder | patterns | `" " * a + "*" * b` | dsa/04 |
| Two variables | remember last two | `a, b = b, a + b` | dsa/03 |
| Two indexes | walk two places | `i`, `j` in a `while` | dsa/07 |
| Seen-set | repeats | `if x in seen: ...; seen.add(x)` | dsa/09 |
| Counter-dict | frequencies | `c[x] = c.get(x, 0) + 1` | dsa/10 |
| Group-dict | bucket items | `g.setdefault(k, []).append(x)` | dsa/10 |
| Remember-seen | value -> index | `if target - n in seen` | dsa/10 |
| Sort with key | custom order | `sorted(x, key=f)` | dsa/11 |
| Stack (list) | last in, first out | `append` / `pop` | dsa/12 |

## Picking a pattern
- Repeat or first repeat? Seen-set.
- How many of each? Counter-dict.
- Biggest or smallest? Best so far.
- Many lookups? Dict or set.
- Two lists or two ends? Two indexes.
