import os
import pandas as pd
from dotenv import load_dotenv

from config import DATA_DIR
from src.collect.spotify import SpotifyEnricher

load_dotenv()


def main() -> None:
    genius_path = DATA_DIR / "checkpoint_genius.csv"
    if not genius_path.exists():
        print("Genius checkpoint не найден. Сначала запусти make collect-genius.")
        return

    client_id = os.environ["SPOTIPY_CLIENT_ID"]
    client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]

    df = pd.read_csv(genius_path)
    print(f"Загружено {len(df)} треков из Genius checkpoint")

    enricher = SpotifyEnricher(
        client_id=client_id,
        client_secret=client_secret,
        checkpoint_path=DATA_DIR / "checkpoint_spotify.csv",
    )
    enricher.enrich(df)


if __name__ == "__main__":
    main()
