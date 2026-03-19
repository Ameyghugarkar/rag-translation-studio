import json

# Load translation memory
def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Retrieve translation
def retrieve(text):
    data = load_data()

    for entry in data:
        if entry["source"] == text:
            return entry["translation"]

    return None


# Test function
if __name__ == "__main__":
    test_input = "good morning"
    result = retrieve(test_input)

    if result:
        print("Found in memory:", result)
    else:
        print("No match found")