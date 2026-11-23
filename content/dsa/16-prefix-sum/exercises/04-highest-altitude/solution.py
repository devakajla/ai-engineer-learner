def max_altitude(gains):
    altitude = 0
    best = 0
    for g in gains:
        altitude += g
        best = max(best, altitude)
    return best
