import json
from rapidfuzz import fuzz

# Load data
def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Smart retrieval
def retrieve(text):
    data = load_data()

    best_match = None
    highest_score = 0

    for entry in data:
        score = fuzz.ratio(text, entry["source"])

        if score > highest_score:
            highest_score = score
            best_match = entry

    # Threshold (important)
    if highest_score > 70:
        return best_match["translation"], highest_score

    return None, highest_score


# Test
if __name__ == "__main__":
    test_input = "good morning team"
    result, score = retrieve(test_input)

    if result:
        print(f"Match found ({score}%):", result)
    else:
        print("No good match found")