from utils import import_translation


SOURCE_URL = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/fi_finnish.json"
TARGET_TRANSLATION_CODE = "fi_1776"
TARGET_TRANSLATION_NAME = "Biblia 1776"


def import_finnish_translation():
    verse_count = import_translation(SOURCE_URL, TARGET_TRANSLATION_CODE, TARGET_TRANSLATION_NAME)
    print(f"Imported {verse_count} verses for {TARGET_TRANSLATION_CODE}.", flush=True)


if __name__ == "__main__":
    import_finnish_translation()
    print("Imported fi_1776 Bible data.")
