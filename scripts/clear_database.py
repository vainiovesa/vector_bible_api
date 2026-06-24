import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from db import create_tables, drop_tables


def clear_database() -> None:
    print("Dropping database schema...", flush=True)
    drop_tables()
    print("Recreating database schema...", flush=True)
    create_tables()
    print("Database cleared.", flush=True)


if __name__ == "__main__":
    clear_database()
