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


def get_embedding(text):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=MODEL).data[0].embedding


def search_verses(text, limit=5, max_distance=0.9):

    embedding = get_embedding(text)

    with sessionlocal() as session:
        distance = BibleVerse.embedding.cosine_distance(embedding)

        verses = (
            select(BibleVerse)
            .join(Translation)
            .options(joinedload(BibleVerse.translation))
            .where(distance < max_distance)
        )

        return session.scalars(
            verses.order_by(distance).limit(limit)
        ).all()



def get_all_verses():
    with sessionlocal() as session:
        return session.scalars(
            select(BibleVerse).options(joinedload(BibleVerse.translation))
        ).all()
