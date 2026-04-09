# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Context

This directory (`AskAI-Mahabharat/`) is a **data directory** containing sample PDFs used for testing the Streamlit application. The actual application code lives in `/Users/ashish/Sandbox/langchain-ask-pdf/`.

- `data/pdf/Mahabharata.pdf` — 2328-page, ~20MB PDF used as a test document

## Application (langchain-ask-pdf)

### Running

```bash
cd /Users/ashish/Sandbox/langchain-ask-pdf
pip install -r requirements.txt
streamlit run app.py
```

Requires a `.env` file with:
```
OPENAI_API_KEY=your_key_here
OPENAI_ORG_ID=optional_org_id
```

### Architecture

The app implements a **RAG (Retrieval-Augmented Generation)** pipeline in a single file (`app.py`, ~55 lines):

1. **Ingest**: User uploads a PDF → PyPDF2 extracts full text
2. **Chunk**: LangChain `CharacterTextSplitter` splits into 1000-char chunks with 200-char overlap
3. **Embed**: OpenAI Embeddings vectorize each chunk
4. **Store**: FAISS stores vectors in-memory (rebuilt on every upload)
5. **Retrieve**: `similarity_search` finds top-k chunks matching the user's question
6. **Generate**: LangChain `load_qa_chain` (type="stuff") sends retrieved chunks + question to OpenAI LLM

The FAISS index is ephemeral — it is not persisted to disk between sessions. Token usage is logged to stdout via `get_openai_callback`.

### Stack

- Python, Streamlit 1.18.1, LangChain 0.0.154, OpenAI, PyPDF2, FAISS (faiss-cpu)
