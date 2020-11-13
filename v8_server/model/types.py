from typing import List

from sqlalchemy.types import String, TypeDecorator


class IntArray(TypeDecorator):
    impl = String

    def __init__(self, **kwargs) -> None:
        super().__init__(None, **kwargs)

    def process_literal_param(self, value, dialect) -> str:
        # Value will be an int array
        if value is None:
            return ""
        return " ".join(map(str, value))

    process_bind_param = process_literal_param

    def process_result_value(self, value, dialect) -> List[int]:
        # Convert SQL String to Int List
        if value is None:
            return []
        return [int(x) for x in value.split()]
