from fastapi import FastAPI
from pydantic import BaseModel
from db_utils import search_verses, TranslationNotFoundError


class QueryModel(BaseModel):
    query: str
    translation: str


app = FastAPI()


@app.get("/closest_matches/")
def closest_matches(query: str, translation: str, limit: int = 5, max_distance: float = 0.75):
    try:
        matches = search_verses(query, translation, limit, max_distance)
    except TranslationNotFoundError as e:
        return {"error": str(e)}

    return {"query": query,
            "translation": translation,
            "limit": limit,
            "max_distance": max_distance,
            "matches": [
                {
                    "book": verse.book,
                    "chapter": verse.chapter,
                    "verse": verse.verse,
                    "text": verse.text,
                    "distance": dist
                }
                for verse, dist in matches
            ]
        }
