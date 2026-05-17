from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from decimal import Decimal
from typing import Any


def jsonable_value(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, Mapping):
        return {str(key): jsonable_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [jsonable_value(item) for item in value]
    return value


def jsonable_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {str(key): jsonable_value(value) for key, value in row.items()}


def pagination(page: int, page_size: int) -> tuple[int, int]:
    safe_page = max(page, 1)
    safe_page_size = min(max(page_size, 1), 100)
    return safe_page_size, (safe_page - 1) * safe_page_size

