from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from urllib.request import urlopen

from sqlalchemy import delete, insert, select

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from db import create_tables, sessionlocal
from db_utils import get_embeddings
from models import BibleVerse, Translation, Book


BATCH_SIZE = 64


def fetch_bible_data(source_url: str) -> list[dict[str, Any]]:
    with urlopen(source_url) as response:
        return json.load(response)


def ensure_translation_exists(session, code: str, name: str) -> Translation:
    translation = session.scalar(select(Translation).where(Translation.code == code))
    if translation is None:
        print("Translation not found, creating...", flush=True)
        translation = Translation(code=code, name=name)
        session.add(translation)
        session.flush()
        print(f"Created translation: {translation.code} - {translation.name}", flush=True)
    return translation


def chunked(items: list[dict[str, Any]], size: int):
    for start_index in range(0, len(items), size):
        yield items[start_index : start_index + size]


def delete_existing_verses(session, translation_id: int, translation_code: str) -> None:
    print(f"Removing existing {translation_code} verses...", flush=True)
    session.execute(delete(BibleVerse).where(BibleVerse.translation_id == translation_id))


def delete_existing_book_ordering(session):
    print("Removing existing book ordering...", flush=True)
    session.execute(delete(Book))


def build_verse_rows(translation_id: int, book_data: dict[str, Any]) -> list[dict[str, Any]]:
    book_name = book_data["name"]
    verse_rows = []

    for chapter_number, chapter in enumerate(book_data["chapters"], start=1):
        for verse_number, text in enumerate(chapter, start=1):
            verse_rows.append(
                {
                    "translation_id": translation_id,
                    "book": book_name,
                    "chapter": chapter_number,
                    "verse": verse_number,
                    "text": text,
                    "embedding": None,
                }
            )

    for row_batch in chunked(verse_rows, BATCH_SIZE):
        embeddings = get_embeddings([row["text"] for row in row_batch])
        for row, embedding in zip(row_batch, embeddings, strict=True):
            row["embedding"] = embedding

    return verse_rows


def import_book(session, translation: Translation, book_index: int, total_books: int, book_data: dict[str, Any]) -> int:
    book_name = book_data["name"]
    print(f"Importing book {book_index}/{total_books}: {book_name}", flush=True)

    verse_rows = build_verse_rows(translation.id, book_data)
    for row_batch in chunked(verse_rows, BATCH_SIZE):
        session.execute(insert(BibleVerse), row_batch)

    return len(verse_rows)


def import_translation(source_url: str, translation_code: str, translation_name: str) -> int:
    print("Preparing database...", flush=True)
    create_tables()

    print(f"Downloading source data from {source_url}...", flush=True)
    bible_data = fetch_bible_data(source_url)
    print(f"Downloaded {len(bible_data)} books.", flush=True)

    with sessionlocal.begin() as session:
        print(f"Ensuring translation {translation_code} exists...", flush=True)
        translation = ensure_translation_exists(session, translation_code, translation_name)

        delete_existing_verses(session, translation.id, translation.code)

        verse_count = 0
        total_books = len(bible_data)
        for book_index, book_data in enumerate(bible_data, start=1):
            verse_count += import_book(session, translation, book_index, total_books, book_data)

    return verse_count
