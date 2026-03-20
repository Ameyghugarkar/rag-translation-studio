import re

def preprocess(text: str) -> str:
    # lowercase
    text = text.lower()

    # remove special characters
    text = re.sub(r"[^\w\s]", "", text)

    # normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()