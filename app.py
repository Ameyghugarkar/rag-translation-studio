from preprocess import preprocess
from rag import retrieve
from llm import translate

def system_pipeline(text):
    print("\nUser Input:", text)

    # Step 1: Preprocess
    cleaned = preprocess(text)
    print("After preprocessing:", cleaned)

    # Step 2: RAG retrieval
    result, score = retrieve(cleaned)

    if result:
        print(f"RAG Match Found ({score}%):", result)
        return result

    # Step 3: LLM fallback
    print("No good match → Using LLM...")
    llm_output = translate(cleaned)
    return llm_output


# Test
if __name__ == "__main__":
    user_input = input("Enter text: ")
    final_output = system_pipeline(user_input)
    print("\nFinal Translation:", final_output)