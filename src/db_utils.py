import os
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from db import sessionlocal
from models import BibleVerse, Translation


load_dotenv() 


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Environment variable not found: OPENAI_API_KEY")
MODEL = "text-embedding-3-small"


client = OpenAI(api_key=OPENAI_API_KEY)


def get_embedding(text: str):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=MODEL).data[0].embedding


def get_embeddings(texts: list):
    normalized_texts = [text.replace("\n", " ") for text in texts]
    response = client.embeddings.create(input=normalized_texts, model=MODEL)
    return [item.embedding for item in response.data]


def search_verses(text:str, translation:str, limit:int=5, offset:int=0, max_distance:float=0.75):
    with sessionlocal() as session:
        translation_exists = session.scalar(
            select(Translation.id).where(Translation.code == translation)
        )

        if translation_exists is None:
            raise TranslationNotFoundError(f"Translation code not found: {translation}")

        embedding = get_embedding(text)
        distance = BibleVerse.embedding.cosine_distance(embedding)

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


def get_all_verses():
    with sessionlocal() as session:
        return session.scalars(
            select(BibleVerse).options(joinedload(BibleVerse.translation))
        ).all()


def get_all_translations():
    with sessionlocal() as session:
        return session.scalars(select(Translation)).all()


class TranslationNotFoundError(Exception):
    pass
