# Given from earlier exercises. Do not change these.
def model_memory_gb(params_billion, bits):
    return params_billion * bits / 8


def fits_on_gpu(params_billion, bits, gpu_gb, overhead=1.2):
    return model_memory_gb(params_billion, bits) * overhead <= gpu_gb


# Your task:
def pick_quantization(params_billion, gpu_gb, options=(16, 8, 4)):
    for bits in sorted(options, reverse=True):
        if fits_on_gpu(params_billion, bits, gpu_gb):
            return bits
    return None


def plan(models, gpu_gb):
    return {name: pick_quantization(size, gpu_gb) for name, size in models.items()}
