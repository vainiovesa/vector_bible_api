import os
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from db import sessionlocal
from models import BibleVerse, Translation
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


def search_verses(text:str, translation:str, book:str=None, limit:int=5, offset:int=0, max_distance:float=0.75):
    with sessionlocal() as session:
        check_translation_exists(session, translation)

        if book:
            check_book_exists(session, translation, book)

        embedding = get_embedding(text)
        distance = BibleVerse.embedding.cosine_distance(embedding)

        if book:
            stmt = (
                select(BibleVerse, distance.label("distance"))
                .join(Translation)
                .options(joinedload(BibleVerse.translation))
                .order_by(distance)
                .limit(limit)
                .where(
                    distance < max_distance,
                    Translation.code == translation,
                    BibleVerse.book == book
                )
                .offset(offset)
            )
        else:
            stmt = (
                select(BibleVerse, distance.label("distance"))
                .join(Translation)
                .options(joinedload(BibleVerse.translation))
                .order_by(distance)
                .limit(limit)
                .where(
                    distance < max_distance,
                    Translation.code == translation
                )
                .offset(offset)
            )

        results = session.execute(stmt).all()

        return results


def check_translation_exists(session, translation:str):
    translation_exists = session.scalar(
        select(Translation.id).where(Translation.code == translation)
    )

    if translation_exists is None:
        raise TranslationNotFoundError(f"Translation code not found: {translation}")


def check_book_exists(session, translation:str, book:str):
    translation_id = session.scalar(
        select(Translation.id).where(Translation.code == translation)
    )

    book_exists = session.scalar(
        select(BibleVerse.id).where(
            BibleVerse.book == book,
            BibleVerse.translation_id == translation_id
        )
    )
    if book_exists is None:
        raise BookNotFoundError(f"Book not found: {book}")


def get_all_translations():
    with sessionlocal() as session:
        return session.scalars(select(Translation)).all()


def get_all_books():
    with sessionlocal() as session:
        return session.scalars(
            select(BibleVerse.book).distinct()
        ).all()


class TranslationNotFoundError(Exception):
    pass


class BookNotFoundError(Exception):
    pass
