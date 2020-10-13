import logging


logger = logging.getLogger(__name__)


def function_test(x: int) -> int:
    """
    Returns the input value multiplied by 2

    Args:
        x (int): Value to multiply

    Returns:
        int: input value multiplied by 2

    Example:
        >>> function_test(2)
        4
    """
    return x * 2
