from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models import Book, Translation, BibleVerse


def chunked(items: list[dict[str, Any]], size: int):
    for start_index in range(0, len(items), size):
        yield items[start_index : start_index + size]


def delete_existing_book_ordering(session):
    print("Removing existing book ordering...", flush=True)
    session.execute(delete(Book))


def ensure_translation_exists(session, code: str, name: str) -> Translation:
    translation = session.scalar(select(Translation).where(Translation.code == code))
    if translation is None:
        print("Translation not found, creating...", flush=True)
        translation = Translation(code=code, name=name)
        session.add(translation)
        session.flush()
        print(f"Created translation: {translation.code} - {translation.name}", flush=True)
    return translation


def delete_existing_verses(session, translation_id: int, translation_code: str) -> None:
    print(f"Removing existing {translation_code} verses...", flush=True)
    session.execute(delete(BibleVerse).where(BibleVerse.translation_id == translation_id))
