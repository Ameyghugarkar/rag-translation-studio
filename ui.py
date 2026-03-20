import streamlit as st
import json

from preprocess import preprocess
from rag import retrieve
from llm import translate


# -----------------------------
# SAVE FUNCTION
# -----------------------------
def save_translation(source, translation):
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append({
        "source": source,
        "translation": translation
    })

    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Translation Studio",
    layout="wide"
)

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
page = st.sidebar.radio(
    "📂 Navigation",
    ["📝 Translate", "📚 History", "⚙️ Settings"]
)


# ============================================================
# 📝 TRANSLATE PAGE
# ============================================================
if page == "📝 Translate":

    st.title("🌍 AI Translation Studio")
    st.caption("⚡ Quick Translate Workspace")

    # -----------------------------
    # 🔥 INPUT PANEL (ALWAYS TOP)
    # -----------------------------
    with st.container():

        col1, col2 = st.columns([3, 1])

        with col1:
            user_input = st.text_area(
                "✏️ Enter text",
                height=100,
                placeholder="Type or paste text here..."
            )

        with col2:
            style = st.selectbox(
                "🎯 Style",
                ["General", "Legal", "Healthcare", "Business", "Casual"]
            )

        if st.button("🚀 Translate"):

            if user_input.strip() == "":
                st.warning("Please enter text")
            else:
                cleaned = preprocess(user_input)

                result, score = retrieve(cleaned)

                if result:
                    output = result
                    st.success(f"RAG Match ({round(score,2)}%)")
                else:
                    output = translate(cleaned, style)

                st.session_state.current = {
                    "input": user_input,
                    "output": output,
                    "style": style
                }

    # -----------------------------
    # 🔥 RESULT PANEL
    # -----------------------------
    st.divider()

    if "current" in st.session_state:

        st.subheader("📌 Result")

        edited = st.text_area(
            "✏️ Edit translation",
            st.session_state.current["output"],
            height=120
        )

        col1, col2 = st.columns(2)

        # SAVE
        with col1:
            if st.button("💾 Save Translation"):
                save_translation(
                    st.session_state.current["input"],
                    edited
                )
                st.success("Saved to memory!")

        # CLEAR
        with col2:
            if st.button("🧹 Clear"):
                st.session_state.pop("current")
                st.rerun()


# ============================================================
# 📚 HISTORY PAGE
# ============================================================
elif page == "📚 History":

    st.title("📚 Translation History")

    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except:
        data = []

    if not data:
        st.info("No translations saved yet.")
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

                        with open("data.json", "w") as f:
                            json.dump(data, f, indent=4)

                        st.success("Updated!")

                # REUSE
                with col2:
                    if st.button("♻️ Use Again", key=f"use_{i}"):

                        st.session_state.current = {
                            "input": item["source"],
                            "output": item["translation"],
                            "style": "General"
                        }

                        st.success("Loaded → Go to Translate tab")


# ============================================================
# ⚙️ SETTINGS PAGE
# ============================================================
elif page == "⚙️ Settings":

    st.title("⚙️ Settings")

    st.markdown("""
    ### 🔧 Coming Soon:
    - 🌐 Select target language  
    - 🤖 Switch LLM model (LLaMA / Phi)  
    - 📄 PDF Translation  
    - 📊 Analytics Dashboard  
    """)

    st.info("More features will be added here.")