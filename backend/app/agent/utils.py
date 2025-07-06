# backend/app/agent/utils.py

import json
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

def safe_json_parse(content: Any) -> dict:
    try:
        if hasattr(content, "model_dump") and callable(content.model_dump):
            content = content.model_dump()
        if isinstance(content, list | dict):
            content = json.dumps(content)
        elif not isinstance(content, str):
            content = str(content)

        return json.loads(content)
    except Exception as e:
        logger.error(f"Could not parse LLM response as JSON: {content} ({e})")
        return {}
