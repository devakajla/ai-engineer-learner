from datetime import date


def days_between(start, end):
    return (date.fromisoformat(end) - date.fromisoformat(start)).days
