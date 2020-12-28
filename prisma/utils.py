import time


def time_since(start: float, precision: int = 4) -> str:
    # TODO: prettier output
    delta = round(time.monotonic() - start, precision)
    return f'{delta}s'
