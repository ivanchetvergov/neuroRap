import os
import shutil
from dotenv import load_dotenv

from artists import ARTIST_LIST
from config import DATA_DIR
from src.collect.genius import GeniusCollector

load_dotenv()


def main() -> None:
    checkpoint_path = DATA_DIR / "checkpoint_genius.csv"
    existing_path = DATA_DIR / "lyrics_df.csv"

    # если checkpoint ещё нет, но старый датасет есть — используем его как стартовую точку
    if not checkpoint_path.exists() and existing_path.exists():
        shutil.copy(existing_path, checkpoint_path)
        import pandas as pd
        n = len(pd.read_csv(checkpoint_path))
        print(f"[seed] checkpoint засидирован из {existing_path} ({n} треков)")

    token = os.environ["GENIUS_ACCESS_TOKEN"]
    collector = GeniusCollector(token=token, checkpoint_path=checkpoint_path)
    df = collector.collect(ARTIST_LIST)
    print(f"Genius: собрано {len(df)} треков")


if __name__ == "__main__":
    main()
