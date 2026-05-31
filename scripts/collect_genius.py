import os
from dotenv import load_dotenv

from artists import ARTIST_LIST
from config import DATA_DIR
from src.collect.genius import GeniusCollector

load_dotenv()


def main() -> None:
    token = os.environ["GENIUS_ACCESS_TOKEN"]
    collector = GeniusCollector(
        token=token,
        checkpoint_path=DATA_DIR / "checkpoint_genius.csv",
    )
    # обходит артистов с начала списка → вперёд
    df = collector.collect(ARTIST_LIST)
    print(f"Genius: собрано {len(df)} треков")


if __name__ == "__main__":
    main()
