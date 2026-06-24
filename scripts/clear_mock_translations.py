from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import delete, select

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from db import sessionlocal
from models import BibleVerse, Translation


MOCK_TRANSLATION_CODES = ("mock-en", "mock-es")


def clear_mock_translations() -> None:
    print("Clearing mock translations...", flush=True)
    with sessionlocal.begin() as session:
        mock_translation_ids = select(Translation.id).where(Translation.code.in_(MOCK_TRANSLATION_CODES))
        session.execute(delete(BibleVerse).where(BibleVerse.translation_id.in_(mock_translation_ids)))
        session.execute(delete(Translation).where(Translation.code.in_(MOCK_TRANSLATION_CODES)))
    print("Mock translations cleared.", flush=True)


if __name__ == "__main__":
    clear_mock_translations()
