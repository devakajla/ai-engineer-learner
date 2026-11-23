def parse_age(text):
    try:
        age = int(text)
    except ValueError:
        raise ValueError("age must be a number")
    if age < 0 or age > 150:
        raise ValueError("age out of range")
    return age
