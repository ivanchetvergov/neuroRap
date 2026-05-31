from dataclasses import dataclass
from typing import Optional


@dataclass
class SongData:
    artist: str
    title: str
    lyrics: str
    structured_text: str
    tags: str
    primary_artist: str
    album: Optional[str]
