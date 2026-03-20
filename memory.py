import json
import os
from difflib import SequenceMatcher

DATA_FILE = "data.json"
GLOSSARY_FILE = "glossary.json"


# ---------------- LOAD / SAVE ---------------- #

def load_memory():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------------- ADD TRANSLATION ---------------- #

def add_translation(source, translation, style):
    data = load_memory()

    data.append({
        "source": source.lower(),
        "translation": translation,
        "style": style,
        "approved": True
    })

    save_memory(data)


# ---------------- SIMILARITY ---------------- #

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


# ---------------- EXACT MATCH ---------------- #

def exact_match(query, style):
    data = load_memory()

    for item in data:
        if item["source"] == query.lower() and item["style"] == style:
            return item["translation"], 95

    return None, 0


# ---------------- FUZZY MATCH ---------------- #

def fuzzy_match(query, style, threshold=0.75):
    data = load_memory()

    best_match = None
    best_score = 0

    for item in data:
        if item["style"] != style:
            continue

        score = similarity(query.lower(), item["source"])

        if score > best_score:
            best_score = score
            best_match = item

    if best_match and best_score >= threshold:
        return best_match["translation"], int(best_score * 100)

    return None, 0


# ---------------- GLOSSARY ---------------- #

def load_glossary():
    if not os.path.exists(GLOSSARY_FILE):
        return {}
    with open(GLOSSARY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def apply_glossary(text):
    glossary = load_glossary()

    for word, replacement in glossary.items():
        text = text.replace(word, replacement)

    return text


# ---------------- MAIN PIPELINE ---------------- #

def retrieve_translation(query, style):
    result, confidence = exact_match(query, style)
    if result:
        return result, "RAG", confidence

    result, confidence = fuzzy_match(query, style)
    if result:
        return result, "RAG-FUZZY", confidence

    return None, "LLM", 0


def memory_pipeline(query, style):
    translation, source, confidence = retrieve_translation(query, style)

    if translation:
        translation = apply_glossary(translation)

    return {
        "translation": translation,
        "source": source,
        "confidence": confidence
    }