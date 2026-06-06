import re


def clean_lyrics(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"Embed$", "", text, flags=re.MULTILINE).strip()
    text = re.sub(r"^\d+Embed$", "", text, flags=re.MULTILINE).strip()
    # normalize section headers whitespace: [ Куплет 1 ] → [Куплет 1]
    text = re.sub(r"\[\s*(.*?)\s*\]", r"[\g<1>]", text)
    # strip non-lyric characters but preserve newlines
    text = re.sub(r"[^a-zA-Z0-9\n\r\.,:;?!\-'—«»()а-яА-ЯёЁ\[\] ]+", " ", text)
    # collapse multiple spaces (but not newlines)
    text = re.sub(r"[ \t]+", " ", text)
    # collapse 3+ blank lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
