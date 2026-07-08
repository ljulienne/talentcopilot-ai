import re


class TextCleaner:
    def clean(self, text: str) -> str:
        text = text or ""
        text = text.replace("\u00a0", " ")
        text = text.replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
