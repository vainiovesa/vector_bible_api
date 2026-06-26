from fastapi import FastAPI
from db_utils import search_verses, get_all_translations, get_all_books, search_chunks, verses_of_chunk, TranslationNotFoundError, BookNotFoundError


app = FastAPI()


@app.get("/closest_matches/")
def closest_matches(query: str, translation: str, book: str = None, limit: int = 5, offset: int = 0, max_distance: float = 0.75):
    try:
        matches = search_verses(query, translation, book, limit, offset, max_distance)
    except TranslationNotFoundError as e:
        return {"error": str(e)}
    except BookNotFoundError as e:
        return {"error": str(e)}

    return {"query": query,
            "translation": translation,
            "book": book,
            "limit": limit,
            "offset": offset,
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


@app.get("/closest_chunks/")
def closest_chunks(query: str, translation: str, book: str = None, limit: int = 5, offset: int = 0, max_distance: float = 0.75):
    try:
        matches = search_chunks(query, translation, book, limit, offset, max_distance)
    except TranslationNotFoundError as e:
        return {"error": str(e)}
    except BookNotFoundError as e:
        return {"error": str(e)}

    result = []
    for chunk, dist in matches:
        verses = verses_of_chunk(chunk)
        result.append({
            "distance": dist,
            "verses": [
                {
                    "book": verse.book,
                    "chapter": verse.chapter,
                    "verse": verse.verse,
                    "text": verse.text
                }
                for verse in verses
            ]
        })

    return {
        "query": query,
        "translation": translation,
        "book": book,
        "limit": limit,
        "offset": offset,
        "max_distance": max_distance,
        "matches": result
    }


@app.get("/translations/")
def get_translations():
    translations = get_all_translations()
    return {"translations": [{"code": t.code, "name": t.name} for t in translations]}


@app.get("/books/")
def get_books():
    books = get_all_books()
    return [{"name": book} for book in books]
