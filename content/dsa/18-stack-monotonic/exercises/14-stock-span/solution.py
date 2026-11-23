def stock_spans(prices):
    result = []
    stack = []
    for i, p in enumerate(prices):
        while stack and prices[stack[-1]] <= p:
            stack.pop()
        result.append(i - stack[-1] if stack else i + 1)
        stack.append(i)
    return result
