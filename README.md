# LinguaForge — AI Translation Studio

> An AI-powered translation studio that remembers every translation your team approves and reuses it automatically.

---

## What is LinguaForge?

LinguaForge is a local, privacy-first translation tool built for enterprise workflows. It combines **RAG (Retrieval-Augmented Generation)** with a local LLM to eliminate redundant translation work, enforce consistent terminology, and continuously improve from human corrections — all without sending your data to any external API.

---

## Features

- **RAG Translation Memory** — language-aware fuzzy matching (0.82 threshold) surfaces previously approved translations instantly
- **Glossary Enforcement** — domain-specific terms (e.g. `client → cliente`) are applied automatically before every translation
- **Local LLM via Ollama** — uses `phi` model, zero per-query API cost, nothing leaves your machine
- **PDF Upload & Translation** — full document translation with live chunk progress
- **Auto Language Detection** — detects source language automatically using `langdetect`
- **Translation History** — every approved translation is saved, searchable, editable, and reusable
- **Continuous Learning** — human-approved corrections are saved back to memory, improving future translations
- **13+ Languages** — English, French, Spanish, German, Hindi, Chinese, Japanese, Arabic, Portuguese, Russian, Korean, Italian, and more

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| LLM | Ollama (`phi` model) |
| RAG | SequenceMatcher fuzzy matching |
| Language Detection | `langdetect` |
| PDF Processing | PyMuPDF (`fitz`) |
| Storage | `data.json`, `glossary.json` |
| Language | Python 3 |

---

## Project Structure

```
rag-translation-studio/
├── ui.py              # Streamlit frontend — all pages and UI
├── llm.py             # Ollama phi integration + prompt injection defense
├── rag.py             # RAG retrieval and translation memory
├── glossary.py        # Glossary management
├── preprocess.py      # Text cleaning and normalization
├── pdf_handler.py     # PDF extraction and cleaning
├── memory.py          # Memory pipeline
├── data.json          # Translation history store
├── glossary.json      # Domain term pairs
└── requirements.txt
```

---

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and start Ollama

Download from [ollama.com](https://ollama.com) then run:

```bash
ollama pull phi
ollama serve
```

### 3. Run the app

```bash
python -m streamlit run ui.py
```

App opens at **http://localhost:8501**

---

## How It Works

```
User Input
    ↓
Preprocess (clean + normalize)
    ↓
Glossary Apply (enforce domain terms)
    ↓
RAG Lookup (check translation memory)
    ↓ hit                    ↓ miss
Return approved       LLM Translate (Ollama phi)
translation                 ↓
    ↓              Human Review + Edit
    └──────────────────────↓
                   Save to Memory
                   (improves future translations)
```

---

## Pages

| Page | Description |
|---|---|
| ⚡ Translate | Main translation interface with RAG + LLM hybrid pipeline |
| 📄 PDF Upload | Upload and translate full PDF documents |
| 📚 Glossary | Add, edit, and export domain-specific term pairs |
| 🕑 History | Browse, search, edit, load, and delete past translations |

---

## Built For

****
Problem Statement: AI-Powered Translation Studio
Domain: Enterprise AI / NLP


