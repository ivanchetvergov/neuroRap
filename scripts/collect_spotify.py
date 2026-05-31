import os
from dotenv import load_dotenv

from artists import ARTIST_LIST
from config import DATA_DIR
from src.collect.spotify import SpotifyEnricher

load_dotenv()


def main() -> None:
    client_id = os.environ["SPOTIPY_CLIENT_ID"]
    client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]

    enricher = SpotifyEnricher(
        client_id=client_id,
        client_secret=client_secret,
        checkpoint_path=DATA_DIR / "checkpoint_spotify.csv",
    )
    # обходит артистов с конца списка → навстречу Genius-у
    enricher.run(
        genius_checkpoint=DATA_DIR / "checkpoint_genius.csv",
        artist_list=ARTIST_LIST,
    )


if __name__ == "__main__":
    main()
