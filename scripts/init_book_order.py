import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from db import create_tables, sessionlocal
from models import Book
from script_utils import delete_existing_book_ordering


def init_book_order() -> None:
    create_tables()

    with sessionlocal.begin() as session:
        delete_existing_book_ordering(session)

        print("Initializing book order...", flush=True)
        book_order_file = PROJECT_ROOT / "scripts" / "data" / "book_order.csv"
        with open(book_order_file, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("Order"):
                    continue
                parts = line.split(",")
                if len(parts) < 3:
                    print(f"Skipping invalid line: {line}", flush=True)
                    continue
                canonical_order = int(parts[0])
                name = parts[1]
                testament = parts[2].strip().lower()
                old_testament = testament == "old"
                book = Book(canonical_order=canonical_order, name=name, old_testament=old_testament)
                session.add(book)


if __name__ == "__main__":
    init_book_order()
    print("Added book ordering to db.")
