def days_until_warmer(temps):
    answer = [0] * len(temps)
    stack = []
    for i, t in enumerate(temps):
        while stack and t > temps[stack[-1]]:
            j = stack.pop()
            answer[j] = i - j
        stack.append(i)
    return answer
