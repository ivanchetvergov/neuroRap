import re

import pandas as pd
from transformers import AutoTokenizer


class RapDataTokenizer:
    _SECTION_PATTERNS = {
        "INTRO": r"\[Интро[^\]]*\]",
        "VERSE": r"\[Куплет[^\]]*\]",
        "CHORUS": r"\[Припев[^\]]*\]",
        "BRIDGE": r"\[Bridge[^\]]*\]",
        "OUTRO": r"\[Аутро[^\]]*\]",
    }

    def __init__(self, base_model: str = "sberbank-ai/rugpt3small_based_on_gpt2"):
        self.tokenizer = AutoTokenizer.from_pretrained(base_model)
        self._add_special_tokens()

    def _add_special_tokens(self) -> None:
        self.tokenizer.add_special_tokens({
            "additional_special_tokens": [
                "<META>", "</META>",
                "<LYRICS>", "</LYRICS>",
                "<SEC>", "</SEC>",
                "<VERSE>", "<CHORUS>", "<BRIDGE>", "<INTRO>", "<OUTRO>",
            ]
        })
        self.tokenizer.pad_token = self.tokenizer.eos_token

    def extract_sections(self, lyrics: str) -> list[tuple[str, str]]:
        positions: list[tuple[int, str, str]] = []
        for section_type, pattern in self._SECTION_PATTERNS.items():
            for match in re.finditer(pattern, lyrics, re.IGNORECASE):
                positions.append((match.start(), section_type, match.group()))
        positions.sort()

        sections: list[tuple[str, str]] = []
        for i, (pos, sec_type, header) in enumerate(positions):
            start = pos + len(header)
            end = positions[i + 1][0] if i + 1 < len(positions) else len(lyrics)
            content = lyrics[start:end].strip()
            if content:
                sections.append((sec_type, content))
        return sections

    def structure_row(self, row: pd.Series) -> str:
        artist = str(row.get("artist", "Unknown"))
        tags_raw = str(row.get("tags", ""))
        tags = [t.strip() for t in tags_raw.split(",")[:3] if t.strip()] or ["Hip-Hop"]

        meta = f"<META> [{artist}] [{', '.join(tags)}] </META>"

        lyrics = str(row.get("lyrics", ""))
        sections = self.extract_sections(lyrics)

        if not sections:
            clean = re.sub(r"\[.*?\]", "", lyrics).strip()
            lyrics_block = f"<LYRICS>\n<SEC><VERSE>\n{clean}\n</SEC>\n</LYRICS>"
        else:
            parts = []
            for sec_type, content in sections:
                clean = re.sub(r"\[.*?\]", "", content).strip()
                if clean:
                    parts.append(f"<SEC><{sec_type}>\n{clean}\n</SEC>")
            lyrics_block = "<LYRICS>\n" + "\n".join(parts) + "\n</LYRICS>"

        eos = self.tokenizer.eos_token or ""
        return f"{meta}\n{lyrics_block}{eos}"

    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        result["tokenized_text"] = result.apply(self.structure_row, axis=1)
        avg_len = result["tokenized_text"].str.len().mean()
        print(f"Обработано: {len(result)} строк, средняя длина: {avg_len:.0f} символов")
        return result

    def create_generation_prompt(self, artist: str, tags: list[str], section: str = "VERSE") -> str:
        meta = f"<META> [{artist}] [{', '.join(tags[:3])}] </META>"
        return f"{meta}\n<LYRICS>\n<SEC><{section.upper()}>\n"
