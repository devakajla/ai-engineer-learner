def lora_params(d_in, d_out, rank):
    if rank < 1:
        raise ValueError("rank must be at least 1")
    full = d_in * d_out
    lora = rank * (d_in + d_out)
    return {"full": full, "lora": lora, "percent": round(100 * lora / full, 2)}
