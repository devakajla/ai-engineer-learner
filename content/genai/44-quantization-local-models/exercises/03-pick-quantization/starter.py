# Given from earlier exercises. Do not change these.
def model_memory_gb(params_billion, bits):
    return params_billion * bits / 8


def fits_on_gpu(params_billion, bits, gpu_gb, overhead=1.2):
    return model_memory_gb(params_billion, bits) * overhead <= gpu_gb


# Your task:
def pick_quantization(params_billion, gpu_gb, options=(16, 8, 4)):
    ...


def plan(models, gpu_gb):
    ...
