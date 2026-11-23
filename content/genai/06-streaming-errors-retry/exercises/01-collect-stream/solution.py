def collect_stream(stream):
    pieces = []
    for chunk in stream:
        if not chunk.choices:
            continue
        piece = chunk.choices[0].delta.content
        if piece:
            pieces.append(piece)
    return "".join(pieces)
