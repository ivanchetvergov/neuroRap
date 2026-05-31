import time
from typing import Optional

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

AUDIO_FEATURES = ["tempo", "energy", "valence", "danceability", "loudness", "speechiness"]


class SpotifyEnricher:
    def __init__(self, client_id: str, client_secret: str):
        self._sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret,
            ),
            requests_timeout=10,
        )

    def enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        for col in AUDIO_FEATURES:
            result[col] = None

        for idx, row in result.iterrows():
            features = self._get_features(str(row["artist"]), str(row["title"]))
            if features:
                for col, val in features.items():
                    result.at[idx, col] = val
            time.sleep(0.1)

        n_enriched = result["energy"].notna().sum()
        print(f"Spotify: обогащено {n_enriched}/{len(result)} треков")
        return result

    def _get_features(self, artist: str, title: str) -> Optional[dict]:
        try:
            res = self._sp.search(q=f"artist:{artist} track:{title}", type="track", limit=1)
            items = res["tracks"]["items"]
            if not items:
                return None

            track_id = items[0]["id"]
            features = self._sp.audio_features([track_id])[0]
            if not features:
                return None

            return {k: features[k] for k in AUDIO_FEATURES if k in features}
        except Exception as e:
            print(f"  [spotify] '{artist} — {title}': {e}")
            return None
