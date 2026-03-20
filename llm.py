import requests


# -----------------------------
# CHUNKING (FIXED)
# -----------------------------
def chunk_text(text, size=6):
    words = text.split()
    chunks = []

    for i in range(0, len(words), size):
        chunk = " ".join(words[i:i+size])
        chunks.append(chunk)

    return chunks


# -----------------------------
# STYLE PROMPTS
# -----------------------------
def get_style_prompt(style, text):

    if style == "Legal":
        return f"Translate into formal legal Spanish:\n{text}"

    elif style == "Healthcare":
        return f"Translate into professional medical Spanish:\n{text}"

    elif style == "Business":
        return f"Translate into professional business Spanish:\n{text}"

    elif style == "Casual":
        return f"Translate into casual conversational Spanish:\n{text}"

    else:
        return f"Translate into Spanish:\n{text}"


# -----------------------------
# LLM TRANSLATION (OLLAMA PHI)
# -----------------------------
def translate(text, style="General"):

    prompt = get_style_prompt(style, text)

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi",   # your working model
                "prompt": prompt,
                "stream": False
            }
        )

        if response.status_code == 200:
            result = response.json()["response"].strip()

            # clean bad outputs
            if len(result) == 0:
                return "Translation error"

            return result

        else:
            return "Translation error"

    except Exception as e:
        print("LLM ERROR:", e)
        return "Translation error"