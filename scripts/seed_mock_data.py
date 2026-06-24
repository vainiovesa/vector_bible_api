import sys
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from db import create_tables, sessionlocal
from db_utils import get_embedding
from clear_mock_translations import clear_mock_translations
from models import BibleVerse, Translation


MOCK_TRANSLATIONS = [
    {
        "code": "mock-en",
        "name": "Mock English",
        "verses": [
            ("Genesis", 1, 1, "In the beginning, light and form were made."),
            ("John", 1, 1, "In the beginning was the Word, and the Word was with God, and the Word was God."),
            ("Psalms", 23, 1, "The Lord is my shepherd; I shall not want."),
        ],
    },
    {
        "code": "mock-es",
        "name": "Mock Spanish",
        "verses": [
            ("Genesis", 1, 1, "En el principio, la luz y la forma fueron hechas."),
            ("Juan", 1, 1, "En el principio era el Verbo, y el Verbo era con Dios, y el Verbo era Dios."),
            ("Salmos", 23, 1, "El Senor es mi pastor; nada me faltara."),
        ],
    },
]


def seed_mock_data() -> None:
    create_tables()
    clear_mock_translations()

    with sessionlocal.begin() as session:
        for translation_data in MOCK_TRANSLATIONS:
            translation = Translation(
                code=translation_data["code"],
                name=translation_data["name"],
            )
            session.add(translation)
            session.flush()

            verses: Iterable[tuple[str, int, int, str]] = translation_data["verses"]
            for book, chapter, verse, text in verses:
                session.add(
                    BibleVerse(
                        translation_id=translation.id,
                        book=book,
                        chapter=chapter,
                        verse=verse,
                        text=text,
                        embedding=get_embedding(f"{translation.code}:{book}:{chapter}:{verse}:{text}"),
                    )
                )


if __name__ == "__main__":
    seed_mock_data()
    print("Seeded mock Bible data.")
