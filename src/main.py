from fastapi import FastAPI
from db_utils import (
    search_verses,
    get_all_translations,
    translation_is_chunked,
    get_books_of_translation,
    get_name_of_translation,
    get_testament_of_book,
    get_number_of_verses,
    search_chunks,
    verses_of_chunk,
    TranslationNotFoundError,
    TestamentNotFoundError,
    BookNotFoundError,
    FilterOptionError,
    NotChunkedError
)


app = FastAPI()


@app.get("/closest_matches/")
def closest_matches(query: str, translation: str, testament: str = None, book: str = None, limit: int = 5, offset: int = 0, max_distance: float = 0.75):
    try:
        matches = search_verses(query, translation, testament, book, limit, offset, max_distance)
    except (
        TranslationNotFoundError,
        TestamentNotFoundError,
        BookNotFoundError,
        FilterOptionError
    ) as e:
        return {"error": str(e)}

    return {"query": query,
            "translation": translation,
            "testament": testament,
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
def closest_chunks(query: str, translation: str, testament: str = None, book: str = None, limit: int = 5, offset: int = 0, max_distance: float = 0.75):
    try:
        matches = search_chunks(query, translation, testament, book, limit, offset, max_distance)
    except (
        TranslationNotFoundError,
        TestamentNotFoundError,
        BookNotFoundError,
        FilterOptionError,
        NotChunkedError
    ) as e:
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
        "testament": testament,
        "book": book,
        "limit": limit,
        "offset": offset,
        "max_distance": max_distance,
        "matches": result
    }


@app.get("/translations/")
def get_translations():
    translations = get_all_translations()
    return [
        {
            "code": t.code,
            "name": t.name
        }
        for t in translations
    ]


@app.get("/translation_info/")
def translation_info(translation: str):
    try:
        name = get_name_of_translation(translation)
        is_chunked = translation_is_chunked(translation)
        books = get_books_of_translation(translation)
        num_verses = get_number_of_verses(translation)
    except TranslationNotFoundError as e:
        return {"error": str(e)}

    return {
        "code": translation,
        "name": name,
        "chunked": is_chunked,
        "num_verses": num_verses,
        "books": [
            {
                "name": book,
                "testament": get_testament_of_book(book)}
            for book in books
        ]
    }
