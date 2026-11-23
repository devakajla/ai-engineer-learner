def status_text(code):
    match code:
        case 200:
            return "OK"
        case 201:
            return "Created"
        case 400 | 422:
            return "Client error"
        case 404:
            return "Not found"
        case x if 500 <= x <= 599:
            return "Server error"
        case _:
            return "Unknown"
