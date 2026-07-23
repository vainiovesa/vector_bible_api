import argparse
import sys
from pathlib import Path

from sqlalchemy import delete, select

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from db import sessionlocal
from models import BibleVerse, Translation


def remove_translation(translation_code) -> None:
    print(f"Removing {translation_code}...", flush=True)
    with sessionlocal.begin() as session:
        translation_id = select(Translation.id).where(Translation.code == translation_code)
        session.execute(delete(BibleVerse).where(BibleVerse.translation_id == translation_id))
        session.execute(delete(Translation).where(Translation.code == translation_code))
    print(f"{translation_code} removed.", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove translation from the database by code.")
    parser.add_argument("translation_code", help="E.g. 'en_kjv'")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    remove_translation(args.translation_code)
