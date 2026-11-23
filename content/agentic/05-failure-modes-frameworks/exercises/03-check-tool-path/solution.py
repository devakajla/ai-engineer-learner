def check_tool_path(expected, actual):
    position = 0
    for name in actual:
        if position < len(expected) and name == expected[position]:
            position += 1
    extra = []
    for name in actual:
        if name not in expected and name not in extra:
            extra.append(name)
    return {
        "all_called": all(name in actual for name in expected),
        "in_order": position == len(expected),
        "extra": extra,
    }
