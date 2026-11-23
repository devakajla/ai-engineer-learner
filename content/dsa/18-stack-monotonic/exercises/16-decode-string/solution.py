def decode_string(s):
    stack = []
    current = ""
    number = 0
    for ch in s:
        if ch.isdigit():
            number = number * 10 + int(ch)
        elif ch == "[":
            stack.append((current, number))
            current = ""
            number = 0
        elif ch == "]":
            previous, times = stack.pop()
            current = previous + current * times
        else:
            current += ch
    return current
