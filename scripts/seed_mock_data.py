import sys
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from db import create_tables, sessionlocal
from db_utils import get_embeddings
from clear_mock_translations import clear_mock_translations
from models import BibleVerse, Translation


MOCK_TRANSLATIONS = [
    {
        "code": "mock-en",
        "name": "Mock English",
        "verses": [
            ("Genesis", 1, 1, "In the beginning God created the heavens and the earth."),
            ("Genesis", 1, 2, "Now the earth was formless and empty, darkness was over the surface of the deep, and the Spirit of God was hovering over the waters."),
            ("Genesis", 1, 3, "And God said, “Let there be light,” and there was light."),
            ("Genesis", 1, 4, "God saw that the light was good, and he separated the light from the darkness."),
            ("Genesis", 1, 5, "God called the light “day,” and the darkness he called “night.” And there was evening, and there was morning—the first day."),
            ("Genesis", 1, 6, "And God said, “Let there be a vault between the waters to separate water from water.”"),
            ("Genesis", 1, 7, "So God made the vault and separated the water under the vault from the water above it. And it was so."),
            ("Genesis", 1, 8, "God called the vault “sky.” And there was evening, and there was morning—the second day."),
            ("John", 1, 1, "In the beginning was the Word, and the Word was with God, and the Word was God."),
            ("John", 1, 2, "He was with God in the beginning."),
            ("John", 1, 3, "Through him all things were made; without him nothing was made that has been made."),
            ("John", 1, 4, "In him was life, and that life was the light of all mankind."),
            ("John", 1, 5, "The light shines in the darkness, and the darkness has not overcome it."),
            ("Psalms", 23, 1, "The Lord is my shepherd, I lack nothing."),
            ("Psalms", 23, 2, "He makes me lie down in green pastures, he leads me beside quiet waters,"),
            ("Psalms", 23, 3, "he refreshes my soul. He guides me along the right paths for his name's sake."),
            ("Psalms", 23, 4, "Even though I walk through the darkest valley, I will fear no evil, for you are with me; your rod and your staff, they comfort me."),
            ("Psalms", 23, 5, "You prepare a table before me in the presence of my enemies. You anoint my head with oil; my cup overflows."),
            ("Psalms", 23, 6, "Surely your goodness and love will follow me all the days of my life, and I will dwell in the house of the Lord forever."),
        ]
    },
    {
        "code": "mock-es",
        "name": "Mock Spanish",
        "verses": [
            ("Genesis", 1, 1, "En el principio creó Dios los cielos y la tierra."),
            ("Genesis", 1, 2, "Y la tierra estaba desordenada y vacía, y las tinieblas estaban sobre la faz del abismo, y el Espíritu de Dios se movía sobre la faz de las aguas."),
            ("Genesis", 1, 3, "Y dijo Dios: Sea la luz; y fue la luz."),
            ("Genesis", 1, 4, "Y vio Dios que la luz era buena; y separó Dios la luz de las tinieblas."),
            ("Genesis", 1, 5, "Y llamó Dios a la luz Día, y a las tinieblas llamó Noche. Y fue la tarde y la mañana un día."),
            ("Genesis", 1, 6, "Luego dijo Dios: Haya expansión en medio de las aguas, y separe las aguas de las aguas."),
            ("Genesis", 1, 7, "E hizo Dios la expansión, y separó las aguas que estaban debajo de la expansión, de las aguas que estaban sobre la expansión. Y fue así."),
            ("Genesis", 1, 8, "Y llamó Dios a la expansión Cielos. Y fue la tarde y la mañana el día segundo."),
            ("Juan", 1, 1, "En el principio era el Verbo, y el Verbo era con Dios, y el Verbo era Dios."),
            ("Juan", 1, 2, "Este era en el principio con Dios."),
            ("Juan", 1, 3, "Todas las cosas por él fueron hechas, y sin él nada de lo que ha sido hecho, fue hecho."),
            ("Juan", 1, 4, "En él estaba la vida, y la vida era la luz de los hombres."),
            ("Juan", 1, 5, "La luz en las tinieblas resplandece, y las tinieblas no prevalecieron contra ella."),
            ("Juan", 1, 6, "Hubo un hombre enviado de Dios, el cual se llamaba Juan."),
            ("Salmos", 23, 1, "Jehová es mi pastor; nada me faltará."),
            ("Salmos", 23, 2, "En lugares de delicados pastos me hará descansar; Junto a aguas de reposo me pastoreará."),
            ("Salmos", 23, 3, "Confortará mi alma; Me guiará por sendas de justicia por amor de su nombre."),
            ("Salmos", 23, 4, "Aunque ande en valle de sombra de muerte, No temeré mal alguno, porque tú estarás conmigo; Tu vara y tu cayado me infundirán aliento."),
            ("Salmos", 23, 5, "Aderezas mesa delante de mí en presencia de mis angustiadores; Unges mi cabeza con aceite; mi copa está rebosando."),
            ("Salmos", 23, 6, "Ciertamente el bien y la misericordia me seguirán todos los días de mi vida, Y en la casa de Jehová moraré por largos días."),
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

            embeddings = get_embeddings([text for _, _, _, text in translation_data["verses"]])

            verses: Iterable[tuple[str, int, int, str]] = translation_data["verses"]
            for book, chapter, verse, text in verses:
                session.add(
                    BibleVerse(
                        translation_id=translation.id,
                        book=book,
                        chapter=chapter,
                        verse=verse,
                        text=text,
                        embedding=embeddings.pop(0),
                    )
                )


if __name__ == "__main__":
    seed_mock_data()
    print("Seeded mock Bible data.")
