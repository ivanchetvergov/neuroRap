from dataclasses import dataclass
from typing import Optional


@dataclass
class SongData:
    artist: str
    title: str
    lyrics: str
    tags: str
    album: Optional[str]
