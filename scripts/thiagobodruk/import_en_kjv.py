from utils import import_translation


SOURCE_URL = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/en_kjv.json"
TARGET_TRANSLATION_CODE = "en_kjv"
TARGET_TRANSLATION_NAME = "King James Version"


def import_english_translation():
    verse_count = import_translation(SOURCE_URL, TARGET_TRANSLATION_CODE, TARGET_TRANSLATION_NAME)
    print(f"Imported {verse_count} verses for {TARGET_TRANSLATION_CODE}.", flush=True)


if __name__ == "__main__":
    import_english_translation()
    print("Imported en_kjv Bible data.")
