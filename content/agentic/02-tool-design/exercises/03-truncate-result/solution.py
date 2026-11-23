def truncate_result(text, max_chars):
    if len(text) <= max_chars:
        return text
    more = len(text) - max_chars
    return text[:max_chars] + f"\n[truncated {more} more characters]"
