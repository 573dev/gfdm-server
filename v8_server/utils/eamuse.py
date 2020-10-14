from time import time


def get_timestamp() -> str:
    """
    Make a timestamp int for logging purposes
    """
    return str(int(round(time() * 1000)))
