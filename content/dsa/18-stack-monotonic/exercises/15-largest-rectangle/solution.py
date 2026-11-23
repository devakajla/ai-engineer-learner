def largest_rectangle(heights):
    stack = []
    best = 0
    bars = heights + [0]
    for i, h in enumerate(bars):
        while stack and bars[stack[-1]] > h:
            height = bars[stack.pop()]
            left = stack[-1] if stack else -1
            best = max(best, height * (i - left - 1))
        stack.append(i)
    return best
