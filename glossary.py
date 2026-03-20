import json
import os

GLOSSARY_FILE = "glossary.json"


# ---------------- LOAD ---------------- #

def load_glossary():
    if not os.path.exists(GLOSSARY_FILE):
        return {}
    with open(GLOSSARY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------- APPLY ---------------- #

def apply_glossary(text):
    glossary = load_glossary()

    for word, replacement in glossary.items():
        text = text.replace(word, replacement)

    return text


# ---------------- ADD TERM ---------------- #

def add_term(source, target):
    glossary = load_glossary()
    glossary[source] = target

    with open(GLOSSARY_FILE, "w", encoding="utf-8") as f:
        json.dump(glossary, f, indent=2)


# ---------------- DELETE TERM ---------------- #

def delete_term(source):
    glossary = load_glossary()

    if source in glossary:
        del glossary[source]

        with open(GLOSSARY_FILE, "w", encoding="utf-8") as f:
            json.dump(glossary, f, indent=2)