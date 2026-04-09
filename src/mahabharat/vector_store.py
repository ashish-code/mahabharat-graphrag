"""FAISS vector store for passage retrieval."""
import os
import pickle
from typing import List, Dict, Tuple
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from .config import FAISS_INDEX_PATH

_embeddings = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        print("Loading embedding model (all-MiniLM-L6-v2)...")
        _embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )
    return _embeddings


def build_vector_store(chunks: List[Dict]) -> FAISS:
    """Build FAISS index from text chunks."""
    docs = [
        Document(
            page_content=c["text"],
            metadata={"chunk_id": c["id"], "start_page": c["start_page"]},
        )
        for c in chunks
    ]
    print(f"Building FAISS index over {len(docs)} chunks...")
    store = FAISS.from_documents(docs, get_embeddings())
    store.save_local(FAISS_INDEX_PATH)
    print(f"FAISS index saved to {FAISS_INDEX_PATH}")
    return store


def load_vector_store() -> FAISS:
    """Load persisted FAISS index."""
    store = FAISS.load_local(
        FAISS_INDEX_PATH,
        get_embeddings(),
        allow_dangerous_deserialization=True,
    )
    print("FAISS index loaded")
    return store


def similarity_search(store: FAISS, query: str, k: int = 5) -> List[str]:
    """Return top-k passage texts for a query."""
    docs = store.similarity_search(query, k=k)
    return [d.page_content for d in docs]
