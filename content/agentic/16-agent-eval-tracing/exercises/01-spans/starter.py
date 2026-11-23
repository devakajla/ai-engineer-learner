def add_span(trace, name, kind, start, end, **attrs):
    ...


def trace_summary(trace):
    ...


def traced_call(trace, name, kind, clock, fn, *args, **kwargs):
    ...
