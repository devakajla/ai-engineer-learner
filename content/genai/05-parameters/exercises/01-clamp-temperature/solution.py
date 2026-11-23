def clamp_temperature(t):
    if t < 0:
        return 0.0
    if t > 2:
        return 2.0
    return float(t)
