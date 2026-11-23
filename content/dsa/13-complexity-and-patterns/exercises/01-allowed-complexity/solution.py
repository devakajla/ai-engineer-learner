def allowed_complexity(n):
    if n <= 10:
        return "O(n!)"
    if n <= 20:
        return "O(2^n)"
    if n <= 500:
        return "O(n^3)"
    if n <= 5000:
        return "O(n^2)"
    if n <= 10**6:
        return "O(n log n)"
    if n <= 10**8:
        return "O(n)"
    return "O(log n)"
