import logging
import time
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import lyricsgenius as lg
import pandas as pd

from artists import ALBUM_TAGS, ARTIST_DEFAULT_TAGS
from src.collect.cleaner import clean_lyrics
from src.schema import SongData

log = logging.getLogger(__name__)


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
        self._checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        existing_df, done_artists = self._load_checkpoint()

        n_total = len(artist_list)
        log.info("Артистов: %d | пропускаем: %d | собираем: %d",
                 n_total, len(done_artists), n_total - len(done_artists))

        for i, artist_name in enumerate(artist_list, 1):
            if artist_name in done_artists:
                log.info("[%2d/%d] %s — пропущен", i, n_total, artist_name)
                continue

            log.info("[%2d/%d] %s", i, n_total, artist_name)
            try:
                log.info("  ищу артиста на Genius...")
                artist_obj = self._genius.search_artist(
                    artist_name, max_songs=max_songs, sort="popularity"
                )
                if not artist_obj:
                    log.warning("  не найден на Genius")
                    continue

                n_songs = len(artist_obj.songs)
                log.info("  найдено %d треков, начинаю сбор", n_songs)
                songs: list[SongData] = []

                for j, song in enumerate(artist_obj.songs, 1):
                    title = song.title[:60]
                    result = self._process_song(song, artist_name)
                    if result:
                        songs.append(result)
                    log.info("  [%3d/%d] %s %s", j, n_songs, title, "✓" if result else "✗")
                    time.sleep(0.15)

                log.info("  готово: %d/%d треков | в базе: %d",
                         len(songs), n_songs, len(existing_df) + len(songs))

                artist_df = pd.DataFrame([asdict(s) for s in songs])
                existing_df = pd.concat([existing_df, artist_df], ignore_index=True)
                self._save_checkpoint(existing_df)

            except Exception as e:
                log.error("  ошибка при сборе %s: %s", artist_name, e)
                time.sleep(10)

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

            tags = self._get_tags(artist_name, album_name)

            return SongData(
                artist=artist_name,
                title=song_full.title,
                lyrics=lyrics,
                tags=",".join(tags),
                album=album_name,
            )
        except Exception as e:
            log.error("  ошибка трека '%s': %s", song_light.title, e)
            return None

    def _load_checkpoint(self) -> tuple[pd.DataFrame, set[str]]:
        self._merge_legacy_checkpoint()

        if self._checkpoint_path.exists():
            df = pd.read_csv(self._checkpoint_path)
            done = set(df["artist"].unique())
            log.info("[checkpoint] загружено %d треков (%d артистов)", len(df), len(done))
            return df, done
        return pd.DataFrame(), set()

    def _merge_legacy_checkpoint(self) -> None:
        """Однократная миграция из checkpoint_genius.csv → lyrics_df.csv."""
        legacy = self._checkpoint_path.parent / "checkpoint_genius.csv"
        if not legacy.exists():
            return

        old_df = pd.read_csv(legacy)
        if self._checkpoint_path.exists():
            current_df = pd.read_csv(self._checkpoint_path)
            done = set(current_df["artist"].unique())
            extra = old_df[~old_df["artist"].isin(done)]
            if not extra.empty:
                merged = pd.concat([current_df, extra], ignore_index=True)
                merged.to_csv(self._checkpoint_path, index=False)
                log.info("[migrate] добавлено %d треков от %d артистов из checkpoint_genius.csv",
                         len(extra), extra["artist"].nunique())
        else:
            old_df.to_csv(self._checkpoint_path, index=False)
            log.info("[migrate] создан checkpoint из checkpoint_genius.csv (%d треков)", len(old_df))

        legacy.unlink()
        log.info("[migrate] checkpoint_genius.csv удалён")

    def _save_checkpoint(self, df: pd.DataFrame) -> None:
        df.to_csv(self._checkpoint_path, index=False)
        log.info("  [checkpoint] сохранено %d треков", len(df))

    @staticmethod
    def _get_tags(artist_name: str, album_name: Optional[str]) -> list[str]:
        album_map = ALBUM_TAGS.get(artist_name, {})
        if album_name and album_name in album_map:
            return album_map[album_name]
        return ARTIST_DEFAULT_TAGS.get(artist_name, [])
