import time
from pathlib import Path
from typing import Optional

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

AUDIO_FEATURES = ["tempo", "energy", "valence", "danceability", "loudness", "speechiness"]


class SpotifyEnricher:
    def __init__(self, client_id: str, client_secret: str, checkpoint_path: Path):
        self._sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret,
            ),
            requests_timeout=10,
        )
        self._checkpoint_path = checkpoint_path

    def run(self, genius_checkpoint: Path, artist_list: list[str]) -> None:
        """Обогащает треки из Genius-чекпоинта, обходя артистов с конца списка."""
        done = self._load_done()

        for artist_name in reversed(artist_list):
            if not genius_checkpoint.exists():
                print(f"[spotify/wait] genius checkpoint не найден, пропускаем {artist_name}")
                continue

            genius_df = pd.read_csv(genius_checkpoint)
            artist_songs = genius_df[genius_df["artist"] == artist_name]

            if artist_songs.empty:
                print(f"[spotify/skip] {artist_name} ещё не собран Genius-ом")
                continue

            new_rows: list[dict] = []
            for _, row in artist_songs.iterrows():
                key = f"{row['artist']}||{row['title']}"
                if key in done:
                    continue
                features = self._get_features(str(row["artist"]), str(row["title"]))
                if features:
                    new_rows.append({"artist": row["artist"], "title": row["title"], **features})
                    done.add(key)
                time.sleep(0.1)

            if new_rows:
                self._save(new_rows)
                print(f"[spotify] {artist_name}: +{len(new_rows)} треков обогащено")
            else:
                print(f"[spotify/done] {artist_name}: всё уже обогащено")

        total = len(pd.read_csv(self._checkpoint_path)) if self._checkpoint_path.exists() else 0
        print(f"\nSpotify итого: {total} треков в чекпоинте")

    def _get_features(self, artist: str, title: str) -> Optional[dict]:
        try:
            res = self._sp.search(q=f"artist:{artist} track:{title}", type="track", limit=1)
            items = res["tracks"]["items"]
            if not items:
                return None
            features = self._sp.audio_features([items[0]["id"]])[0]
            if not features:
                return None
            return {k: features[k] for k in AUDIO_FEATURES if k in features}
        except Exception as e:
            print(f"  [spotify] '{artist} — {title}': {e}")
            return None

    def _load_done(self) -> set[str]:
        if not self._checkpoint_path.exists():
            return set()
        df = pd.read_csv(self._checkpoint_path)
        return set(df["artist"] + "||" + df["title"])

    def _save(self, new_rows: list[dict]) -> None:
        self._checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        df_new = pd.DataFrame(new_rows)
        if self._checkpoint_path.exists():
            df_old = pd.read_csv(self._checkpoint_path)
            df_new = pd.concat([df_old, df_new], ignore_index=True)
        df_new.to_csv(self._checkpoint_path, index=False)
