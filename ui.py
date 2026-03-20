import streamlit as st
import json
from app import system_pipeline
from preprocess import preprocess
from rag import retrieve, save_translation, retrieve_for_chunks
from llm import translate, chunk_text
from glossary import apply_glossary, load_glossary, add_term, delete_term


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AI Translation Studio", layout="wide")

# -----------------------------
# NAVIGATION
# -----------------------------
page = st.sidebar.radio(
    "📂 Navigation",
    ["📝 Translate", "📚 History", "⚙️ Settings"]
)

# ============================================================
# 📝 TRANSLATE
# ============================================================
if page == "📝 Translate":

    st.title("🌍 AI Translation Studio")
    st.caption("⚡ Smart Translation Workspace (Optimized RAG + LLM)")

    col1, col2 = st.columns([3, 1])

    with col1:
        user_input = st.text_area("✏️ Enter text", height=150)

    with col2:
        style = st.selectbox(
            "🎯 Style",
            ["General", "Legal", "Healthcare", "Business", "Casual"]
        )

    # -----------------------------
    # TRANSLATE BUTTON
    # -----------------------------
    if st.button("🚀 Translate"):

        if user_input.strip() == "":
            st.warning("Please enter text")
        else:
            cleaned = preprocess(user_input)

            # ======================================
            # ⚡ SMALL INPUT → FAST PATH
            # ======================================
            if len(cleaned.split()) <= 8:

                from app import system_pipeline

                result = system_pipeline(user_input, style)

                if result:
                    output = result["translation"]
                    source = result["source"]
                    confidence = result["confidence"]

                    st.success(f"{source} | Confidence: {confidence}%")

                else:
                    output = translate(cleaned, style)
                    output = apply_glossary(output)

                    source = f"LLM ({style})"
                    confidence = 70

                    st.info("Used LLM fallback")

            # ======================================
            # 🧠 LARGE INPUT → CHUNK RAG
            # ======================================
            else:

                chunks = chunk_text(cleaned)

                # DEBUG (optional)
                # st.write("Chunks:", chunks)

                rag_results = retrieve_for_chunks(chunks)

                final_output = []
                total_confidence = 0

                for res in rag_results:

                    # ✅ RAG HIT
                    if res.get("translation"):
                        translated = res["translation"]
                        total_confidence += res["confidence"]

                    # ❌ LLM FALLBACK
                    else:
                        translated = translate(res["chunk"], style)
                        total_confidence += 70

                    translated = apply_glossary(translated)
                    final_output.append(translated)

                output = " ".join(final_output)
                confidence = round(total_confidence / len(rag_results), 2)
                source = "Hybrid (Chunk RAG + LLM)"

                st.success(f"{source} | Confidence: {confidence}%")

            # STORE RESULT
            st.session_state.current = {
                "input": user_input,
                "output": output,
                "style": style,
                "source": source,
                "confidence": confidence
            }

    # -----------------------------
    # RESULT SECTION
    # -----------------------------
    st.divider()

    if "current" in st.session_state:

        st.subheader("📌 Result")

        edited = st.text_area(
            "✏️ Edit translation",
            st.session_state.current["output"],
            height=180
        )

        st.caption(
            f"Source: {st.session_state.current['source']} | Confidence: {st.session_state.current['confidence']}%"
        )

        col1, col2 = st.columns(2)

        # SAVE
        with col1:
            if st.button("💾 Save Translation"):
                save_translation(
                    st.session_state.current["input"],
                    edited,
                    st.session_state.current["style"]
                )
                st.success("Saved to memory!")

        # CLEAR
        with col2:
            if st.button("🧹 Clear"):
                st.session_state.pop("current")
                st.rerun()


# ============================================================
# 📚 HISTORY
# ============================================================
elif page == "📚 History":

    st.title("📚 Translation History")

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = []

    if not data:
        st.info("No translations yet.")
    else:
        for i, item in enumerate(data):

            with st.expander(f"📝 {item['source']}"):

                edited = st.text_area(
                    "Edit translation",
                    item["translation"],
                    key=f"hist_{i}"
                )

                col1, col2 = st.columns(2)

                # UPDATE
                with col1:
                    if st.button("🔄 Update", key=f"update_{i}"):
                        data[i]["translation"] = edited

                        with open("data.json", "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=4, ensure_ascii=False)

                        st.success("Updated!")

                # REUSE
                with col2:
                    if st.button("♻️ Use Again", key=f"use_{i}"):

                        st.session_state.current = {
                            "input": item["source"],
                            "output": item["translation"],
                            "style": "General",
                            "source": "Memory",
                            "confidence": 100
                        }

                        st.success("Loaded → Go to Translate tab")


# ============================================================
# ⚙️ SETTINGS (GLOSSARY)
# ============================================================
elif page == "⚙️ Settings":

    st.title("⚙️ Glossary Management")

    glossary = load_glossary()

    st.subheader("➕ Add Term")

    col1, col2 = st.columns(2)

    with col1:
        source = st.text_input("Source word")

    with col2:
        target = st.text_input("Target translation")

    if st.button("Add Term"):
        if source and target:
            add_term(source, target)
            st.success("Added!")
            st.rerun()
        else:
            st.warning("Fill both fields")

    st.divider()

    st.subheader("📚 Existing Terms")

    if not glossary:
        st.info("No glossary yet")
    else:
        for key, value in glossary.items():

            col1, col2, col3 = st.columns([3, 3, 1])

            with col1:
                st.write(f"**{key}**")

            with col2:
                st.write(f"→ {value}")

            with col3:
                if st.button("❌", key=key):
                    delete_term(key)
                    st.rerun()