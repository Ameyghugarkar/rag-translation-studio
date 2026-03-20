import json

FILE = "glossary.json"


# -----------------------------
# LOAD GLOSSARY
# -----------------------------
def load_glossary():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


# -----------------------------
# SAVE GLOSSARY
# -----------------------------
def save_glossary(glossary):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(glossary, f, indent=4, ensure_ascii=False)


# -----------------------------
# ADD TERM
# -----------------------------
def add_term(source, target):
    glossary = load_glossary()
    glossary[source.lower()] = target
    save_glossary(glossary)


# -----------------------------
# DELETE TERM
# -----------------------------
def delete_term(source):
    glossary = load_glossary()
    if source.lower() in glossary:
        del glossary[source.lower()]
        save_glossary(glossary)


# -----------------------------
# APPLY GLOSSARY
# -----------------------------
def apply_glossary(text):
    glossary = load_glossary()

    words = text.split()
    corrected = []

    for word in words:
        lower = word.lower()

        if lower in glossary:
            corrected.append(glossary[lower])
        else:
            corrected.append(word)

    return " ".join(corrected)