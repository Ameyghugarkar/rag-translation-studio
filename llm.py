import requests

# -----------------------------
# TRANSLATION FUNCTION
# -----------------------------
def translate(text, style="General", target_language="Spanish"):
    """
    Translate text using local LLM (Ollama)
    """

    # 🔥 STRICT PROMPT (prevents leakage)
    prompt = f"""
You are a translator.

Translate to {target_language} in {style} style.

Output ONLY the final translation.
NO explanation.
NO extra text.

Text: {text}
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi",   # you can switch to llama3 later
                "prompt": prompt,
                "stream": False
            }
        )

        result = response.json()

        if "response" not in result:
            return "⚠️ No response from model."

        output = result["response"].strip()

        # -----------------------------
        # 🔥 CLEAN OUTPUT (VERY IMPORTANT)
        # -----------------------------

        # remove unwanted parts
        if "Text:" in output:
            output = output.split("Text:")[0]

        # remove extra lines
        if "\n" in output:
            output = output.split("\n")[0]

        # remove quotes if any
        output = output.strip('"')

        return output.strip()

    except Exception as e:
        return f"❌ Error: {str(e)}"


# -----------------------------
# TEST
# -----------------------------
if __name__ == "__main__":
    print("🔹 Testing LLM...\n")

    test_cases = [
        ("take medicine twice a day", "Healthcare"),
        ("legal proceedings start tomorrow", "Legal"),
        ("good morning team", "General")
    ]

    for text, style in test_cases:
        print(f"Input: {text} ({style})")
        print("Output:", translate(text, style))
        print("-" * 40)