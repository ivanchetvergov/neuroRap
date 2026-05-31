import re


def clean_generated_lyrics(raw_output: str) -> list[str]:
    text = re.sub(r"<META>.*?</META>", "", raw_output, flags=re.DOTALL)
    text = text.replace("<LYRICS>", "").replace("</LYRICS>", "")

    def _replace_section(match: re.Match) -> str:
        mapping = {
            "VERSE": "Куплет",
            "CHORUS": "Припев",
            "BRIDGE": "Бридж",
            "INTRO": "Интро",
            "OUTRO": "Аутро",
        }
        key = match.group(1).upper()
        return f"\n\n[{mapping.get(key, key.capitalize())}]\n"

    text = re.sub(r"<SEC><(VERSE|CHORUS|BRIDGE|INTRO|OUTRO)>", _replace_section, text, flags=re.IGNORECASE)
    text = text.replace("</SEC>", "")
    text = re.sub(r"<[A-Z_/]+>", "", text)
    text = re.sub(r"([.?!])\s+", r"\1\n", text)
    text = re.sub(r"(,\s+)([А-ЯЁA-Z])", r",\n\2", text)
    text = re.sub(r"(\n\s*){3,}", "\n\n", text).strip()

    return text.split("\n")
