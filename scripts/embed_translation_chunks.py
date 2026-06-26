import argparse
import sys
from pathlib import Path

from sqlalchemy import delete, insert, or_, select

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from db import create_tables, sessionlocal
from db_utils import get_embeddings
from script_utils import chunked
from models import BibleChunk, BibleVerse, Translation


EMBEDDING_BATCH_SIZE = 64
DEFAULT_CHUNK_SIZE = 5
DEFAULT_WINDOW_STEP = 2


def build_chunk_text(verses: list[BibleVerse]) -> str:
    formatted = []
    for verse in verses:
        formatted.append(verse.text)
    return " ".join(formatted)


def get_translation(session, translation_code: str) -> Translation:
    translation = session.scalar(select(Translation).where(Translation.code == translation_code))
    if translation is None:
        raise ValueError(f"Translation code not found: {translation_code}")
    return translation


def get_translation_verses(session, translation_id: int) -> list[BibleVerse]:
    return list(
        session.scalars(
            select(BibleVerse)
            .where(BibleVerse.translation_id == translation_id)
            .order_by(BibleVerse.id)
        )
    )


def delete_existing_chunks_for_translation(session, translation_id: int) -> None:
    verse_ids_stmt = select(BibleVerse.id).where(BibleVerse.translation_id == translation_id)
    session.execute(
        delete(BibleChunk).where(
            or_(
                BibleChunk.begin_verse_id.in_(verse_ids_stmt),
                BibleChunk.end_verse_id.in_(verse_ids_stmt),
            )
        )
    )


def build_chunks(verses: list[BibleVerse], chunk_size: int, window_step: int) -> list[dict]:
    rows = []

    current_book_verses = []
    current_book = None

    def add_book_rows(book_verses: list[BibleVerse]) -> None:
        if not book_verses:
            return

        book_length = len(book_verses)

        if book_length <= chunk_size:
            start_indices = [0]
        else:
            last_start_index = book_length - chunk_size
            start_indices = list(range(0, last_start_index + 1, window_step))
            if start_indices[-1] != last_start_index:
                start_indices.append(last_start_index)

        for start_index in start_indices:
            window = book_verses[start_index:start_index + chunk_size]
            rows.append(
                {
                    "begin_verse_id": window[0].id,
                    "end_verse_id": window[-1].id,
                    "embedding": None,
                    "chunk_text": build_chunk_text(window),
                }
            )

    for verse in verses:
        if current_book is None:
            current_book = verse.book

        if verse.book != current_book:
            add_book_rows(current_book_verses)
            current_book_verses = []
            current_book = verse.book

        current_book_verses.append(verse)

    add_book_rows(current_book_verses)

    return rows


def add_embeddings(chunk_rows: list[dict]) -> None:
    for row_batch in chunked(chunk_rows, EMBEDDING_BATCH_SIZE):
        texts = [row["chunk_text"] for row in row_batch]
        embeddings = get_embeddings(texts)
        for row, embedding in zip(row_batch, embeddings, strict=True):
            row["embedding"] = embedding


def insert_chunk_rows(session, chunk_rows: list[dict]) -> None:
    db_rows = [
        {
            "begin_verse_id": row["begin_verse_id"],
            "end_verse_id": row["end_verse_id"],
            "embedding": row["embedding"],
        }
        for row in chunk_rows
    ]

    for row_batch in chunked(db_rows, EMBEDDING_BATCH_SIZE):
        session.execute(insert(BibleChunk), row_batch)


def embed_translation_chunks(translation_code: str, chunk_size: int, window_step: int) -> int:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if window_step <= 0:
        raise ValueError("window_step must be greater than 0")

    print("Preparing database...", flush=True)
    create_tables()

    with sessionlocal.begin() as session:
        translation = get_translation(session, translation_code)
        verses = get_translation_verses(session, translation.id)

        print(f"Found {len(verses)} verses for {translation.code}.", flush=True)
        print(f"Removing existing chunks for {translation.code}...", flush=True)
        delete_existing_chunks_for_translation(session, translation.id)

        print(
            f"Building chunks with size={chunk_size} and window_step={window_step}...",
            flush=True,
        )
        chunk_rows = build_chunks(verses, chunk_size, window_step)
        if not chunk_rows:
            print("No chunks generated.", flush=True)
            return 0

        print(f"Embedding {len(chunk_rows)} chunks...", flush=True)
        add_embeddings(chunk_rows)

        print(f"Inserting {len(chunk_rows)} chunks...", flush=True)
        insert_chunk_rows(session, chunk_rows)

    return len(chunk_rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build rolling Bible chunks for a translation and store their embeddings."
    )
    parser.add_argument(
        "translation",
        help="Translation code (for example: en_kjv or fi_1776).",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help=f"Number of verses per chunk (default: {DEFAULT_CHUNK_SIZE}).",
    )
    parser.add_argument(
        "--window-step",
        type=int,
        default=DEFAULT_WINDOW_STEP,
        help=f"Rolling window step in verses (default: {DEFAULT_WINDOW_STEP}).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    chunk_count = embed_translation_chunks(args.translation, args.chunk_size, args.window_step)
    print(
        f"Created {chunk_count} chunks for translation {args.translation} "
        f"(chunk_size={args.chunk_size}, window_step={args.window_step}).",
        flush=True,
    )
