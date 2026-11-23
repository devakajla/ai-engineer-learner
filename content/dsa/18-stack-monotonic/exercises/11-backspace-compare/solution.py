def backspace_compare(s, t):
    def build(text):
        stack = []
        for ch in text:
            if ch == "#":
                if stack:
                    stack.pop()
            else:
                stack.append(ch)
        return stack

    return build(s) == build(t)
