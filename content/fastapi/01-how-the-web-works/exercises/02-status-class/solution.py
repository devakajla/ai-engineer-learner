CLASSES = {1: "informational", 2: "success", 3: "redirect", 4: "client_error", 5: "server_error"}


def status_class(code):
    if not 100 <= code <= 599:
        raise ValueError(f"not an HTTP status code: {code}")
    return CLASSES[code // 100]
