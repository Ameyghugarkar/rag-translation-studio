import json
from difflib import SequenceMatcher


DATA_FILE = "data.json"


# -----------------------------
# LOAD DATA
# -----------------------------
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# -----------------------------
# SAVE DATA
# -----------------------------
def save_translation(source, translation, style):

    data = load_data()

    data.append({
        "source": source.lower(),
        "translation": translation,
        "style": style,
        "approved": True
    })

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# -----------------------------
# BASIC SIMILARITY
# -----------------------------
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


# -----------------------------
# ENHANCED SIMILARITY (FIXED)
# -----------------------------
def enhanced_similarity(a, b):
    base = similarity(a, b)

    a_words = set(a.split())
    b_words = set(b.split())

    overlap = len(a_words & b_words) / max(len(a_words), 1)

    return (0.7 * base) + (0.3 * overlap)


# -----------------------------
# RETRIEVE (AGGRESSIVE)
# -----------------------------
def retrieve(text, threshold=0.5):

    data = load_data()
    text = text.lower()

    best_match = None
    best_score = 0

    for item in data:

        score = enhanced_similarity(text, item["source"])

        if score > best_score:
            best_score = score
            best_match = item

    # DEBUG
    print(f"[RAG] Checking: {text}")
    print(f"[RAG] Best score: {best_score}")

    if best_match and best_score >= threshold:

        return {
            "translation": best_match["translation"],
            "source": "RAG Match",
            "confidence": round(best_score * 100, 2)
        }

    return None


# -----------------------------
# CHUNK-LEVEL RETRIEVAL
# -----------------------------
def retrieve_for_chunks(chunks):

    results = []

    for chunk in chunks:

        res = retrieve(chunk)

        if res:
            results.append(res)
        else:
            results.append({
                "chunk": chunk,
                "translation": None,
                "confidence": 0
            })

    return results