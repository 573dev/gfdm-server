def bool_to_int(value: bool) -> int:
    """
    Convert a boolean to an integer.

    True = 1, False = 0
    """
    return 1 if value else 0


def int_to_bool(value: int) -> bool:
    """
    Convert an integer to a boolean.

    1 = True, 0 = False
    """
    return False if value == 0 else True
