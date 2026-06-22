from fastapi import FastAPI
from pydantic import BaseModel


class QueryModel(BaseModel):
    query: str
    translation: str


app = FastAPI()


@app.get("/closest_matches/")
def closest_matches(query: str, translation: str):
    # Fetch closest matches from the vector database based on the query
    return {"query": query,
            "translation": translation,
            "matches": [
                {"book": "John", "chapter": 1, "verse": 1, "text": "Example match 1", "similarity": 0.95},
                {"book": "Genesis", "chapter": 1, "verse": 1, "text": "Example match 2", "similarity": 0.90},
                {"book": "Psalms", "chapter": 23, "verse": 1, "text": "Example match 3", "similarity": 0.85}
            ]
        }
