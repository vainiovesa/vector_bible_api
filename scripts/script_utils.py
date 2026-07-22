from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from sqlalchemy import delete

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models import Book


def chunked(items: list[dict[str, Any]], size: int):
    for start_index in range(0, len(items), size):
        yield items[start_index : start_index + size]


def delete_existing_book_ordering(session):
    print("Removing existing book ordering...", flush=True)
    session.execute(delete(Book))
