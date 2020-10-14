from time import time


def get_timestamp() -> str:
    return str(int(round(time() * 1000)))
