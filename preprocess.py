import re
from textblob import TextBlob

def preprocess(text):
    # Convert to lowercase
    text = text.lower()

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove repeated punctuation
    text = re.sub(r'[!?.]{2,}', '.', text)

    # Spell correction
    corrected = str(TextBlob(text).correct())

    # Manual fix
    if "god morning" in corrected:
        corrected = corrected.replace("god morning", "good morning")

    # Strip spaces
    corrected = corrected.strip()

    return corrected


# Test function
if __name__ == "__main__":
    sample = "  Gud   mornin TEAM!!! "
    print(preprocess(sample))