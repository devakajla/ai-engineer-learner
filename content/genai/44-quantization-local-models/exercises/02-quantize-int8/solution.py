def quantize(values):
    biggest = max((abs(v) for v in values), default=0)
    scale = biggest / 127 if biggest > 0 else 1.0
    return [round(v / scale) for v in values], scale


def dequantize(quantized, scale):
    return [q * scale for q in quantized]


def max_error(values):
    quantized, scale = quantize(values)
    back = dequantize(quantized, scale)
    return max((abs(a - b) for a, b in zip(values, back)), default=0.0)
