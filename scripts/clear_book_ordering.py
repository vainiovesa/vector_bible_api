import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from db import create_tables, sessionlocal
from script_utils import delete_existing_book_ordering


def clear_book_ordering() -> None:
    create_tables()
    print("Clearing book ordering...", flush=True)
    with sessionlocal.begin() as session:
        delete_existing_book_ordering(session)


if __name__ == "__main__":
    clear_book_ordering()
    print("Deleted book ordering from db.")
