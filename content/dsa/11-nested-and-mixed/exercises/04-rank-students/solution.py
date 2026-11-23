def _key(student):
    return (-student["score"], student["name"])


def rank_students(students):
    ordered = sorted(students, key=_key)
    return [s["name"] for s in ordered]
