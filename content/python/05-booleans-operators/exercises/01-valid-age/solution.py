def is_valid_age(age):
    return isinstance(age, int) and not isinstance(age, bool) and 0 <= age <= 120
