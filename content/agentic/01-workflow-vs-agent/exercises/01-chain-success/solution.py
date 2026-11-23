def chain_success(step_success, steps):
    if not 0 <= step_success <= 1:
        raise ValueError("step_success must be between 0 and 1")
    if steps <= 0:
        return 1.0
    return round(step_success ** steps, 4)
