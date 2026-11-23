def unsupported(claims, trusted):
    result = []
    for claim in claims:
        if claim not in trusted:
            result.append(claim)
    return result
