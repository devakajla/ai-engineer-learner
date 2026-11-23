# Complexity and problem patterns (L3+)

## Big-O quick table
Budget: about 10⁸ simple steps. Check `n` first.

| n up to | Allowed |
| --- | --- |
| 10 | O(n!) |
| 20 | O(2ⁿ) |
| 500 | O(n³) |
| 5 000 | O(n²) |
| 10⁶ | O(n log n) |
| 10⁸ | O(n) |

- `x in list` is O(n). `x in set` / `d[k]` is O(1) on average. `sorted()` is O(n log n).
- **Gotcha:** `list.insert(0, x)`, `list.pop(0)` and slicing are O(n).

## Two pointers

**When:** sorted array/string, pair/triplet with a condition, merge, remove, rearrange, "in place", "O(1) space". Not the same as sliding window (a range).

| Type | Template | Examples |
| --- | --- | --- |
| Opposite ends | `l, r = 0, n-1`; `while l < r:` too small -> `l += 1`, too big -> `r -= 1` | Two Sum II, palindrome, container, squares |
| Reader/writer | `slow` writes, `fast` reads: `if keep(nums[fast]): nums[slow] = nums[fast]; slow += 1` | remove duplicates, move zeroes |
| Two lists | `i, j`; append the smaller front item; move that pointer; copy leftovers | merge sorted |
| Fix + pair | sort; `for i`: opposite ends on `i+1..n-1`; skip equal values | 3Sum, 3Sum closest, 4Sum |
| Three pointers | `low, mid, high`; swap into place; after swap with `high` do not move `mid` | Dutch flag |

```python
l, r = 0, len(nums) - 1
while l < r:
    s = nums[l] + nums[r]
    if s == target:
        return [l, r]
    if s < target:
        l += 1
    else:
        r -= 1
# -> O(n) time, O(1) space on a sorted list
```

**Gotchas:** list must be sorted; use `l < r` not `<=`; move at least one pointer every loop; skip duplicates for unique-triplet answers.

## Sliding window

**When:** continuous subarray/substring, longest / shortest / count, with a condition. Positive numbers for sum rules.

| Type | Template | Examples |
| --- | --- | --- |
| Fixed size k | first window, then `total += nums[i] - nums[i-k]` | max sum of k, anagrams, vowels |
| Variable, maximum | add `hi`; `while invalid:` shrink `lo`; then `best = max(best, hi-lo+1)` | no-repeat, k distinct, replacement |
| Variable, minimum | add `hi`; `while valid:` record, shrink `lo` | min subarray >= target, min window |
| Count | after fixing the window, `count += hi - lo + 1` | product < k, at most k distinct |

```python
counts, lo, best = {}, 0, 0
for hi, ch in enumerate(s):
    counts[ch] = counts.get(ch, 0) + 1
    while len(counts) > k:               # invalid
        counts[s[lo]] -= 1
        if counts[s[lo]] == 0:
            del counts[s[lo]]
        lo += 1
    best = max(best, hi - lo + 1)
# -> O(n) time, O(k) space
```

**Gotchas:** `while` not `if`; delete keys at count 0; length is `hi - lo + 1`; negatives break sum windows (use prefix sums); "exactly k" = `at_most(k) - at_most(k-1)`.

## Prefix sum

**When:** many range sums, subarray sum questions (especially with negatives), left/right sums, many range updates.

| Trick | Template |
| --- | --- |
| Range sum | `prefix = [0]`; `prefix.append(prefix[-1] + x)`; sum(l..r) = `prefix[r+1] - prefix[l]` |
| Left / right | `right = total - left - x` |
| Count sum == k | `seen = {0: 1}`; `count += seen.get(total - k, 0)`; then `seen[total] += 1` |
| Longest sum == k | `first = {0: -1}`; `best = i - first[total - k]`; save `total` only if new |
| Divisible by k | key on `total % k`, start `{0: 1}` |
| Equal 0s and 1s | map `0 -> -1`, longest sum 0 |
| Range add | `diff[l] += v; diff[r+1] -= v`, then running sum |
| 2D | `P[i+1][j+1] = m + P[i][j+1] + P[i+1][j] - P[i][j]` |

**Gotchas:** leading `0`; `r + 1` in the formula; `{0: 1}` start; negatives are fine here (not for sliding window).

## Hashmap

**When:** counting, "seen before", pair lookups, grouping, one-to-one matching. Trades O(n) memory for O(n) time.

| Pattern | Template |
| --- | --- |
| Counter-dict | `c[x] = c.get(x, 0) + 1` |
| Need vs have | count both; answer = `min(have[ch] // need[ch])` |
| Seen-dict (Two Sum) | `if target - x in seen: ...` then `seen[x] = i` |
| Group by key | `groups.setdefault(key, []).append(item)` |
| Two dicts | `a -> b` and `b -> a` must both agree |
| Set lookup | start only if `x - 1 not in s`, count up |
| Pair sums | dict of `a + b`, look up `-(c + d)` |

**Gotchas:** check before storing; keys must be hashable (no lists); `del` the key at count 0 if you use `len(d)`.

## Stack and monotonic stack

**When:** matching/nesting, undo, "next greater/smaller", "days until". A Python `list` is the stack: `append`, `pop()`, `stack[-1]`.

| Type | Template |
| --- | --- |
| Plain stack | push openers; on a closer check `stack` not empty and `stack.pop()` matches |
| Next greater | `while stack and nums[stack[-1]] < x: result[stack.pop()] = x`; then `stack.append(i)` |
| Next smaller | same with `>` |
| Distance | when popping `j` at `i`: `result[j] = i - j` |
| Circular | `for i in range(2 * n)`, use `i % n`, push only if `i < n` |
| With count | items `[ch, count]`; pop at `k` |
| Histogram | increasing stack, append a `0` bar to flush |

**Gotchas:** check empty before `pop`; store indexes; `<` vs `<=` with equal values; the stack must be empty at the end for brackets; O(n) because each item is pushed and popped once.

## Kadane

**When:** max/min sum or product of a contiguous part; "best part ending here"; streaks.

| Variant | Template |
| --- | --- |
| Max sum | `ending_here = max(x, ending_here + x)`; `best = max(best, ending_here)`; start from `nums[0]` |
| Min sum | same with `min` |
| Max product | keep `hi` and `lo`; new from `(x, hi*x, lo*x)` |
| One deletion | `deleted = max(keep, deleted + x)` then `keep = max(x, keep + x)` |
| Circular | `max(max_sub, total - min_sub)`; all negative -> `max_sub` |
| Streak | `run = run + 1 if rule else 1` |
| Length >= k | prefix sums with running minimum of `prefix[i-k]` |

**Gotchas:** do not start `best` at 0; parts must be contiguous; update `ending_here` before `best`.

## Intervals

**When:** pairs `[start, end]`: merge, insert, overlap, rooms, free time, cover. First decide if touching counts.

| Task | Template |
| --- | --- |
| Overlap test (closed) | `a <= d and c <= b` |
| Merge | `sorted(iv)`; `if start <= merged[-1][1]: merged[-1][1] = max(...)` else append |
| Insert (sorted) | copy `end < new_start`; merge while `start <= new_end`; copy rest |
| Intersect two lists | `lo = max(starts)`, `hi = min(ends)`; move the pointer that ends first |
| Rooms / max overlap | events `(start, +1)`, `(end, -1)`; sort; running sum max |
| Greedy by end | `sorted((e, s) for s, e in iv)`; keep if `start >= last_end` |
| Free time | `cursor = lo`; gap if `start > cursor`; `cursor = max(cursor, end)` |

**Gotchas:** sort first; take `max(end)`; `<` vs `<=`; copy before editing; do not forget the last gap.

## Binary search

**When:** sorted or rotated data, a shape (peak), or "smallest/largest X such that ..." with a check that flips once.

| Task | Template |
| --- | --- |
| Classic | `lo, hi = 0, n - 1`; `while lo <= hi`; `lo = mid + 1` / `hi = mid - 1` |
| First True / lower bound | `lo, hi = 0, n`; `while lo < hi`; True: `hi = mid`, else `lo = mid + 1` |
| Count of x | `first_ge(x + 1) - first_ge(x)` |
| Peak / mountain | `arr[mid] < arr[mid + 1]`: `lo = mid + 1` else `hi = mid` |
| Rotated | one half is sorted; test if target is inside it |
| On the answer | range `lo..hi` + `works(x)`; min: `works -> hi = mid`; max: `works -> lo = mid + 1` |
| Sorted matrix | chained: `divmod(mid, cols)`; separate: staircase from top-right |

**Gotchas:** do not mix `lo <= hi` and `lo < hi` styles; `lo = mid` loops forever; check the answer range; test empty and one-item input.

## Linked list

**When:** nodes with `.next`: middle, cycle, reverse, n-th from end, merge, rotate.

| Task | Template |
| --- | --- |
| Middle | `slow`/`fast`; `while fast and fast.next` |
| Cycle | `slow is fast` means a cycle; cycle start: restart one pointer at `head` |
| n-th from end | `fast` n steps ahead, then move both |
| Safe edits | `dummy = ListNode(0, head)`; return `dummy.next` |
| Reverse | `nxt = cur.next; cur.next = prev; prev = cur; cur = nxt` |
| Rotate | `k %= n`; make a ring; cut after `n - k - 1` steps |

**Gotchas:** save `.next` first; check `fast` and `fast.next`; empty and one-node lists; return the new head.

## Heap

**When:** top K, K-th largest, always take the best next item, merge sources, medians. Details: `reference/heap-and-deque.md`.

| Task | Template |
| --- | --- |
| K largest | min-heap of size K; push, pop when `len > k`; answer `h[0]` |
| Max-heap | push `-x`, answer `-heappop(h)` |
| Top K frequent | count, push `(-count, item)`, pop K times |
| K-way merge | push `(value, source, index)`; after a pop push the next of that source |
| Greedy | heap of available items; take the best; add newly unlocked items |
| Median | max-heap `low` + min-heap `high`; keep sizes balanced |

**Gotchas:** `heapq` is a min-heap; negate twice; tuples must start with a comparable number; `h` is not sorted.

## Recursion and backtracking

**When:** "all subsets / permutations / combinations", build strings with rules, grid paths, any problem that is the same problem on a smaller input.

| Task | Template |
| --- | --- |
| Recursion | base case first; then solve a smaller input and combine |
| Memoize | `memo = {}`; `if n in memo: return memo[n]`; store before returning |
| Backtracking | choose; `go(next)`; undo (`pop`, `remove`, unmark) |
| Save an answer | `result.append(list(current))` (copy) |
| Subsets | take or skip each item |
| Permutations | `used` flags |
| Combinations | loop from `start`, recurse with `i + 1` |
| Duplicates | sort; `if i > start and a[i] == a[i - 1]: continue` |

**Gotchas:** missing base case; saving a reference not a copy; forgetting undo; recursion depth about 1000.

## Trees and BST

**When:** nodes with `.left` and `.right`: depth, traversals, paths, ancestors, BST rules.

| Task | Template |
| --- | --- |
| Recursion | `if root is None: return base`; combine `f(root.left)` and `f(root.right)` |
| Preorder / inorder / postorder | node first / node between / node last |
| Level order | `deque`; each round `for _ in range(len(queue))` is one level |
| Carry down | pass `remaining` or `(low, high)` to the children |
| Height + best | helper returns height; update `best` with `nonlocal` |
| BST search | `val < node.val`: left; else right |
| BST valid | `low < node.val < high`; left `(low, val)`, right `(val, high)` |
| BST sorted | inorder walk |

**Gotchas:** base case `None`; do not use `root.left.val` without checking; edges vs nodes; ancestors limit a BST node.

## Graphs: BFS and DFS

**When:** connections, groups, grids, "reach", "shortest steps", "number of islands/components". Details for `deque`: `reference/heap-and-deque.md`.

| Task | Template |
| --- | --- |
| Adjacency list | `graph = {i: []}`; append both ways for undirected |
| Grid neighbours | `(r+1, c)`, `(r-1, c)`, `(r, c+1)`, `(r, c-1)` with bounds check |
| DFS | `visited`; `visit(node)`: mark, loop neighbours |
| BFS | `deque([start])`; mark on push; `popleft()` |
| Shortest steps | BFS, one queue round per step |
| Components | `count += 1` for every unvisited start |
| Multi-source | queue all sources first |
| Cycle (undirected) | DFS with `parent` |
| Cycle (directed) | states 0 new, 1 on path, 2 done |

**Gotchas:** visited set; mark on push; both directions for undirected; bounds; do not use DFS for shortest path.

## Graphs: topological sort, Dijkstra, MST

**When:** dependencies and ordering, weighted shortest path, connect everything cheaply, two groups.

| Task | Template |
| --- | --- |
| Topological order | indegree counts, queue of zeros, pop and lower neighbours; `len(order) < n` means cycle |
| Levels / semesters | Kahn, one queue round per level |
| Bipartite | colour 0/1, neighbours get the other colour; same colour means `False` |
| Dijkstra | heap of `(dist, node)`, skip stale pops, relax edges |
| Max along path | Dijkstra with `max(current, edge)` |
| Negative weights | Bellman-Ford: relax all edges n-1 times |
| At most k stops | Bellman-Ford for k+1 rounds on a copy |
| Min spanning tree | Prim: heap of edges leaving the tree |

**Gotchas:** Dijkstra needs weights >= 0; check all components; edge `[a, b]` direction in prerequisites.

## Greedy and intro DP

**Greedy when:** a local best choice stays best. Test with a counter-example. **DP when:** answer builds from overlapping smaller answers (max, min, count, yes/no).

| Task | Template |
| --- | --- |
| Interval scheduling | sort by end, take if `start >= last_end` |
| Jump game | `reach = max(reach, i + nums[i])` |
| Take or skip | `max(skip, take + x)` with two variables |
| Coin change (fewest) | `best[a] = 1 + min(best[a - c])` |
| Coin ways | coin loop outside, amount inside |
| 0/1 knapsack | capacity loop **backwards** |
| LIS | `best[i]` = longest ending at i |
| LCS | 2D table: match `+1`, else max of two neighbours |

**DP recipe:** state, transition, base case, answer cell.
