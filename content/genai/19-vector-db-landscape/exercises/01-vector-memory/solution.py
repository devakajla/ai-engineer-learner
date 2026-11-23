def vector_memory_mb(n_vectors, dim, bytes_per_number=4):
    if n_vectors < 0 or dim < 0 or bytes_per_number < 0:
        raise ValueError("sizes must not be negative")
    total_bytes = n_vectors * dim * bytes_per_number
    return round(total_bytes / 1_000_000, 2)
