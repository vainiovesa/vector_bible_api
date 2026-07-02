import os
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from db import sessionlocal
from models import BibleVerse, Translation, BibleChunk, Book
from cache import get_embedding_from_cache, store_embedding


load_dotenv() 


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Environment variable not found: OPENAI_API_KEY")
MODEL = "text-embedding-3-small"


client = OpenAI(api_key=OPENAI_API_KEY)


def get_embedding(text: str):
    try:
        cached_embedding = get_embedding_from_cache(text)
        if cached_embedding is not None:
            return cached_embedding
    except Exception as e:
        print(f"Error retrieving embedding from cache: {e}")

    text = text.replace("\n", " ")
    embedding = client.embeddings.create(input = [text], model=MODEL).data[0].embedding

    try:
        store_embedding(text, embedding)
    except Exception as e:
        print(f"Error storing embedding in cache: {e}")

    return embedding


def get_embeddings(texts: list):
    normalized_texts = [text.replace("\n", " ") for text in texts]
    response = client.embeddings.create(input=normalized_texts, model=MODEL)
    return [item.embedding for item in response.data]


def search_verses(text:str, translation:str, testament:str=None, book:str=None, limit:int=5, offset:int=0, max_distance:float=0.75):
    with sessionlocal() as session:
        check_translation_exists(session, translation)

        if testament:
            check_if_can_be_filtered_by_testament(session, testament)

        if book:
            check_book_exists(session, book, translation)

        embedding = get_embedding(text)
        distance = BibleVerse.embedding.cosine_distance(embedding)

        stmt = (
            select(BibleVerse, distance.label("distance"))
            .join(Translation)
            .options(joinedload(BibleVerse.translation))
            .where(
                distance < max_distance,
                Translation.code == translation,
            )
        )

        if testament:
            books_of_testament = get_books_of_testament(session, testament)
            stmt = stmt.where(BibleVerse.book.in_(books_of_testament))

        if book:
            stmt = stmt.where(BibleVerse.book == book)

        stmt = stmt.order_by(distance).limit(limit).offset(offset)

        results = session.execute(stmt).all()

        return results


def search_chunks(text:str, translation:str, testament:str=None, book:str=None, limit:int=5, offset:int=0, max_distance:float=0.75):
    with sessionlocal() as session:
        check_translation_exists(session, translation)
        check_translation_is_chunked(translation)

        if testament:
            check_if_can_be_filtered_by_testament(session, testament)

        if book:
            check_book_exists(session, book, translation)

        embedding = get_embedding(text)
        distance = BibleChunk.embedding.cosine_distance(embedding)

        stmt = (
            select(BibleChunk, distance.label("distance"))
            .join(BibleVerse, BibleChunk.begin_verse_id == BibleVerse.id)
            .join(Translation, BibleVerse.translation_id == Translation.id)
            .where(
                distance < max_distance,
                Translation.code == translation,
            )
        )

        if testament:
            books_of_testament = get_books_of_testament(session, testament)
            stmt = stmt.where(BibleVerse.book.in_(books_of_testament))

        if book:
            stmt = stmt.where(BibleVerse.book == book)

        stmt = stmt.order_by(distance).limit(limit).offset(offset)

        results = session.execute(stmt).all()

        return results


def verses_of_chunk(chunk:BibleChunk):
    with sessionlocal() as session:
        verses = session.scalars(
            select(BibleVerse)
            .where(
                BibleVerse.id >= chunk.begin_verse_id,
                BibleVerse.id <= chunk.end_verse_id
            )
            .order_by(BibleVerse.id)
        ).all()
        return verses


def check_translation_exists(session, translation_code:str):
    translation_exists = session.scalar(
        select(Translation.id).where(Translation.code == translation_code)
    )

    if translation_exists is None:
        raise TranslationNotFoundError(f"Translation code not found: '{translation_code}'")


def check_if_can_be_filtered_by_testament(session, testament):
    if testament not in ("old", "new"):
        raise TestamentNotFoundError(f"Testament not found: '{testament}', options: ('old', 'new').")

    if not ordering_exists(session):
        raise FilterOptionError(f"Book ordering table empty; testament cannot be determined.")


def check_book_exists(session, book:str, translation:str=None):
    translation_id = session.scalar(
        select(Translation.id).where(Translation.code == translation)
    )

    stmt = select(BibleVerse.id).where(BibleVerse.book == book)

    if translation:
        stmt = stmt.where(BibleVerse.translation_id == translation_id)

    book_exists = session.scalar(stmt)

    if book_exists is None:
        raise BookNotFoundError(f"Book not found: '{book}'")


def get_all_translations():
    with sessionlocal() as session:
        return session.scalars(select(Translation)).all()


def translation_is_chunked(translation_code:str) -> bool:
    with sessionlocal() as session:
        check_translation_exists(session, translation_code)

        translation = session.scalar(
            select(Translation).where(Translation.code == translation_code)
        )

        chunk_exists = session.scalar(
            select(BibleChunk.id)
            .join(BibleVerse, BibleChunk.begin_verse_id == BibleVerse.id)
            .where(BibleVerse.translation_id == translation.id)
            .limit(1)
        )

        return chunk_exists is not None


def check_translation_is_chunked(translation_code):
    if not translation_is_chunked(translation_code):
        raise NotChunkedError(f"Translation is not chunked: '{translation_code}'")


def get_books_of_translation(translation_code:str) -> list[str]:
    with sessionlocal() as session:
        check_translation_exists(session, translation_code)

        translation = session.scalar(
            select(Translation).where(Translation.code == translation_code)
        )

        if ordering_exists(session):
            stmt = (
                select(BibleVerse.book, Book.canonical_order)
                .join(Book, Book.name == BibleVerse.book)
                .where(BibleVerse.translation_id == translation.id)
                .distinct()
                .order_by(Book.canonical_order)
            )
        else:
            stmt = (
                select(BibleVerse.book)
                .where(BibleVerse.translation_id == translation.id)
                .distinct()
                .order_by(BibleVerse.book)
            )

        books = session.scalars(stmt).all()

        return books


def get_books_of_testament(session, testament):
    old_testament = testament == "old"
    return session.scalars(
        select(Book.name)
        .where(Book.old_testament == old_testament)
    )


def get_name_of_translation(translation_code:str):
    with sessionlocal() as session:
        check_translation_exists(session, translation_code)

        name = session.scalar(
            select(Translation.name).where(Translation.code == translation_code)
        )

        return name


def get_number_of_verses(translation_code:str):
    with sessionlocal() as session:
        check_translation_exists(session, translation_code)

        translation_id = session.scalar(
            select(Translation.id).where(Translation.code == translation_code)
        )

        num = session.scalar(
            select(func.count(BibleVerse.id))
            .where(BibleVerse.translation_id == translation_id)
        )

        return num


def get_testament_of_book(book:str):
    with sessionlocal() as session:
        is_old_testament = session.scalar(
            select(Book.old_testament).where(Book.name == book)
        )

        if is_old_testament is None:
            return

        if is_old_testament:
            return "old"
        return "new"


def ordering_exists(session):
    return session.scalar(select(Book.name).limit(1)) is not None


class TranslationNotFoundError(Exception):
    pass


class TestamentNotFoundError(Exception):
    pass


class BookNotFoundError(Exception):
    pass


class FilterOptionError(Exception):
    pass


class NotChunkedError(Exception):
    pass
