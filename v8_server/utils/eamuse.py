from typing import Dict, Optional


def e_type(_type, count: Optional[int] = None) -> Dict[str, str]:
    result = {"__type": _type}
    if count is not None:
        result["__count"] = str(count)
    return result
