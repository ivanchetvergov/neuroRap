import os
import pandas as pd
from dotenv import load_dotenv

from artists import ARTIST_LIST
from config import DATA_DIR
from src.collect.genius import GeniusCollector

load_dotenv()


def _seed_checkpoint(checkpoint_path, existing_path) -> None:
    """Вливает в checkpoint треки из existing_path, которых там ещё нет (по артисту)."""
    if not existing_path.exists():
        return

    orig = pd.read_csv(existing_path)

    if not checkpoint_path.exists():
        orig.to_csv(checkpoint_path, index=False)
        print(f"[seed] checkpoint создан из {existing_path.name} ({len(orig)} треков)")
        return

    chk = pd.read_csv(checkpoint_path)
    done_artists = set(chk["artist"].unique())
    missing = orig[~orig["artist"].isin(done_artists)]

    if missing.empty:
        return

    merged = pd.concat([chk, missing], ignore_index=True)
    merged.to_csv(checkpoint_path, index=False)
    print(f"[seed] добавлено {len(missing)} треков от {missing['artist'].nunique()} артистов из {existing_path.name}")


def main() -> None:
    checkpoint_path = DATA_DIR / "checkpoint_genius.csv"
    _seed_checkpoint(checkpoint_path, DATA_DIR / "lyrics_df.csv")

    token = os.environ["GENIUS_ACCESS_TOKEN"]
    collector = GeniusCollector(token=token, checkpoint_path=checkpoint_path)
    df = collector.collect(ARTIST_LIST)
    print(f"Genius: {len(df)} треков, {df['artist'].nunique()} артистов")


if __name__ == "__main__":
    main()
