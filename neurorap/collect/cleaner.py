import re


def clean_lyrics(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"Embed$", "", text, flags=re.MULTILINE).strip()
    text = re.sub(r"^\d+Embed$", "", text, flags=re.MULTILINE).strip()
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    text = re.sub(r"\[\s*(.*?)\s*\]", r"[\g<1>]", text)
    text = re.sub(r"[^a-zA-Z0-9\s\.,:;?!\-'—«»()а-яА-ЯёЁ\[\]]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
