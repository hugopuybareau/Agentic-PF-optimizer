# backend/app/agent/utils.py

import logging
from typing import Any

logger = logging.getLogger(__name__)


def clean_value(val: Any) -> str | int | float | bool | str:
    if isinstance(val, str | int | float | bool):
        return val
    elif val is None:
        return ""
    elif isinstance(val, dict):
        return val.get("label") or str(val)
    else:
        return str(val)


def dump(x):
    if hasattr(x, "model_dump"):
        return x.model_dump(mode="json", exclude_none=True)
    if isinstance(x, dict):
        return {k: dump(v) for k, v in x.items()}
    if isinstance(x, list | tuple):
        return [dump(v) for v in x]
    return x
