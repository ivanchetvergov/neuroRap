import os
from dotenv import load_dotenv

from artists import ARTIST_LIST
from config import DATA_DIR
from src.collect.genius import GeniusCollector
from src.collect.spotify import SpotifyEnricher

load_dotenv()


def main() -> None:
    token = os.environ["GENIUS_ACCESS_TOKEN"]
    collector = GeniusCollector(
        token=token,
        checkpoint_path=DATA_DIR / "checkpoint.csv",
    )
    df = collector.collect(ARTIST_LIST)

    spotify_id = os.getenv("SPOTIPY_CLIENT_ID")
    spotify_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    if spotify_id and spotify_secret:
        print("\nSpotify credentials found, enriching audio features...")
        enricher = SpotifyEnricher(spotify_id, spotify_secret)
        df = enricher.enrich(df)
    else:
        print("\nSPOTIPY_CLIENT_ID / SPOTIPY_CLIENT_SECRET not set, skipping audio features.")

    output = DATA_DIR / "lyrics_df.csv"
    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(output, index=False)
    print(f"Сохранено {len(df)} треков → {output}")


if __name__ == "__main__":
    main()
