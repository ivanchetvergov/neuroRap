import time
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import lyricsgenius as lg
import pandas as pd

from artists import ALBUM_TAGS, ARTIST_DEFAULT_TAGS
from src.collect.cleaner import clean_lyrics
from src.schema import SongData


class GeniusCollector:
    def __init__(self, token: str, checkpoint_path: Path):
        self._genius = lg.Genius(
            token,
            remove_section_headers=False,
            skip_non_songs=False,
            excluded_terms=["(Live)", "(Remix)", "(Acoustic)"],
            timeout=60,
            retries=3,
        )
        self._checkpoint_path = checkpoint_path

    def collect(self, artist_list: list[str], max_songs: Optional[int] = None) -> pd.DataFrame:
        existing_df, done_artists = self._load_checkpoint()

        for artist_name in artist_list:
            if artist_name in done_artists:
                print(f"[skip] {artist_name}")
                continue

            print(f"\n--- {artist_name} ---")
            try:
                artist_obj = self._genius.search_artist(artist_name, max_songs=max_songs, sort="popularity")
                if not artist_obj:
                    print("  [!] не найден")
                    continue

                print(f"  найдено {len(artist_obj.songs)} песен")
                songs = []
                for song in artist_obj.songs:
                    result = self._process_song(song, artist_name)
                    if result:
                        songs.append(result)
                    time.sleep(0.15)

                print(f"  собрано: {len(songs)}/{len(artist_obj.songs)}")

                artist_df = pd.DataFrame([asdict(s) for s in songs])
                existing_df = pd.concat([existing_df, artist_df], ignore_index=True)
                self._save_checkpoint(existing_df)

            except Exception as e:
                print(f"  [!] ошибка: {e}")
                time.sleep(10)

        print(f"\nИтого: {len(existing_df)} треков")
        return existing_df

    def _process_song(self, song_light, artist_name: str) -> Optional[SongData]:
        try:
            song_full = self._genius.search_song(song_light.title, artist=artist_name)
            if not song_full:
                return None

            lyrics = clean_lyrics(song_full.lyrics)
            if len(lyrics) < 50:
                return None

            album_name: Optional[str] = None
            if hasattr(song_full, "album") and isinstance(song_full.album, dict):
                album_name = song_full.album.get("name")

            primary_artist = artist_name
            if isinstance(song_full.primary_artist, dict):
                primary_artist = song_full.primary_artist.get("name", artist_name)

            tags = self._get_tags(artist_name, album_name)
            tags_str = ",".join(tags)
            tags_context = f"[TAGS: {tags_str}]" if tags else ""

            structured_text = (
                f"[ARTIST: {artist_name}] [TITLE: {song_full.title}] {tags_context} {lyrics}"
            ).strip()

            return SongData(
                artist=artist_name,
                title=song_full.title,
                lyrics=lyrics,
                structured_text=structured_text,
                tags=tags_str,
                primary_artist=primary_artist,
                album=album_name,
            )
        except Exception as e:
            print(f"  [!] '{song_light.title}': {e}")
            return None

    def _load_checkpoint(self) -> tuple[pd.DataFrame, set[str]]:
        if self._checkpoint_path.exists():
            df = pd.read_csv(self._checkpoint_path)
            done = set(df["artist"].unique())
            print(f"[checkpoint] {len(df)} треков, пропускаем: {done}")
            return df, done
        return pd.DataFrame(), set()

    def _save_checkpoint(self, df: pd.DataFrame) -> None:
        self._checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self._checkpoint_path, index=False)
        print(f"  [checkpoint] {len(df)} треков сохранено")

    @staticmethod
    def _get_tags(artist_name: str, album_name: Optional[str]) -> list[str]:
        album_map = ALBUM_TAGS.get(artist_name, {})
        if album_name and album_name in album_map:
            return album_map[album_name]
        return ARTIST_DEFAULT_TAGS.get(artist_name, [])
