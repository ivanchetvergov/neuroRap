import logging
import os
from dotenv import load_dotenv

from artists import ARTIST_LIST
from config import DATA_DIR
from src.collect.genius import GeniusCollector

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

OUTPUT = DATA_DIR / "lyrics_df.csv"


def main() -> None:
    token = os.environ["GENIUS_ACCESS_TOKEN"]
    # lyrics_df.csv выступает и как seed предыдущего запуска, и как checkpoint текущего
    collector = GeniusCollector(token=token, checkpoint_path=OUTPUT)
    df = collector.collect(ARTIST_LIST)
    log.info("Готово: %d треков, %d артистов → %s", len(df), df["artist"].nunique(), OUTPUT)


if __name__ == "__main__":
    main()
