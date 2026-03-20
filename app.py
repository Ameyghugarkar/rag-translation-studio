from preprocess import preprocess
from rag import retrieve
from llm import translate
from glossary import apply_glossary


def system_pipeline(text, style="General"):
    print("\nUser Input:", text)

    # STEP 1: Preprocess
    cleaned = preprocess(text)
    print("After preprocessing:", cleaned)

    # STEP 2: RAG (Domain 3)
    rag_result = retrieve(cleaned)

    if rag_result:
        print(f"RAG Match Found ({rag_result['confidence']}%)")

        output = apply_glossary(rag_result["translation"])

        return {
            "translation": output,
            "source": "RAG",
            "confidence": rag_result["confidence"]
        }

    # STEP 3: LLM (Domain 2)
    print("No match → Using LLM")

    llm_output = translate(cleaned, style)
    llm_output = apply_glossary(llm_output)

    return {
        "translation": llm_output,
        "source": f"LLM ({style})",
        "confidence": 70
    }


# TEST
if __name__ == "__main__":
    text = input("Enter text: ")
    style = input("Enter style: ")

    result = system_pipeline(text, style)
    print("\nFinal Output:", result)