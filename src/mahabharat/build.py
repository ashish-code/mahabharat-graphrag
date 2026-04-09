"""
Offline pipeline: PDF → chunks → entity/relation extraction → graph + vector index.
Run once: uv run python -m mahabharat.build

Environment variables:
  CHUNK_LIMIT=200   Process only first N chunks (fast dev build, ~5 min)
  CHUNK_LIMIT=0     Process all chunks (full build, ~45-60 min)
"""
import os
import sys
from .config import PDF_PATH, GRAPH_PATH, FAISS_INDEX_PATH
from .ingest import load_pdf, chunk_pages
from .extractor import extract_all
from .seed_data import get_seed_data
from .graph import build_graph, save_graph
from .vector_store import build_vector_store


def main():
    if not os.path.exists(PDF_PATH):
        print(f"ERROR: PDF not found at {PDF_PATH}")
        sys.exit(1)

    from .config import ANTHROPIC_API_KEY
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set. Create a .env file.")
        sys.exit(1)

    print("=" * 60)
    print("Mahabharat Graph RAG — Build Pipeline")
    print("=" * 60)

    # Step 1: Ingest
    print("\n[1/5] Loading PDF...")
    pages = load_pdf(PDF_PATH)

    print("\n[2/5] Chunking text...")
    chunks = chunk_pages(pages)

    limit = int(os.getenv("CHUNK_LIMIT", "0"))
    if limit > 0:
        chunks = chunks[:limit]
        print(f"  (Limited to {limit} chunks via CHUNK_LIMIT env var)")

    # Step 2: Vector store
    print("\n[3/5] Building vector store (local embeddings, no API cost)...")
    build_vector_store(chunks)

    # Step 3: LLM extraction
    print("\n[4/5] Extracting entities and relationships via LLM...")
    extracted_entities, extracted_relations = extract_all(chunks)
    print(f"  Extracted {len(extracted_entities)} entities, {len(extracted_relations)} relationships")

    # Step 4: Merge with pre-verified seed data
    print("\n[5/5] Merging with pre-seeded character graph...")
    seed_entities, seed_relations = get_seed_data()
    all_entities = seed_entities + extracted_entities
    all_relations = seed_relations + extracted_relations
    print(f"  Total: {len(all_entities)} entities, {len(all_relations)} relationships")

    G = build_graph(all_entities, all_relations)
    save_graph(G)

    print("\n" + "=" * 60)
    print("Build complete!")
    print(f"  Graph:        {GRAPH_PATH}")
    print(f"  Vector index: {FAISS_INDEX_PATH}/")
    print("\nRun the app:  uv run streamlit run app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
