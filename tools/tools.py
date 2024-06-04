from typing import Any


def get_nested_value(data: dict, path: str) -> Any:
    keys = path.split('.')
    value = data
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value
