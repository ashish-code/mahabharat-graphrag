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
from .seed_data import get_seed_data
from .graph import build_graph, save_graph
from .inference import apply_all_inference
from .vector_store import build_vector_store


def main():
    if not os.path.exists(PDF_PATH):
        print(f"ERROR: PDF not found at {PDF_PATH}")
        sys.exit(1)

    from .config import get_bedrock_client
    try:
        get_bedrock_client().meta.region_name
    except Exception as e:
        print(f"ERROR: Cannot connect to AWS Bedrock: {e}")
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

    # Step 3: LLM extraction with incremental graph saves
    print("\n[4/5] Extracting entities and relationships via LLM...")
    seed_entities, seed_relations = get_seed_data()
    all_entities = list(seed_entities)
    all_relations = list(seed_relations)

    # Running entity vocabulary for co-reference resolution in subsequent batches
    entity_vocab: set = {e["name"] for e in seed_entities}

    batches = [chunks[i:i + 5] for i in range(0, len(chunks), 5)]
    total = len(batches)
    SAVE_EVERY = 20  # save graph every 20 batches (~100 chunks)

    try:
        for i, batch in enumerate(batches):
            print(f"  Extracting batch {i+1}/{total}...")
            from .extractor import extract_batch
            entities, relations = extract_batch(batch, known_entities=list(entity_vocab))
            entity_vocab.update(e["name"] for e in entities)
            all_entities.extend(entities)
            all_relations.extend(relations)

            # Incremental save so Ctrl+C never loses more than ~2 min of work
            if (i + 1) % SAVE_EVERY == 0:
                G = build_graph(all_entities, all_relations)
                G = apply_all_inference(G)
                save_graph(G)
                print(f"  [checkpoint] Graph saved: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    except KeyboardInterrupt:
        print("\n  Build interrupted — saving progress...")

    # Step 4: Final graph save
    print("\n[5/5] Building and saving final graph...")
    print(f"  Total: {len(all_entities)} entities, {len(all_relations)} relationships")
    G = build_graph(all_entities, all_relations)
    G = apply_all_inference(G)
    save_graph(G)

    print("\n" + "=" * 60)
    print("Build complete!")
    print(f"  Graph:        {GRAPH_PATH}")
    print(f"  Vector index: {FAISS_INDEX_PATH}/")
    print("\nRun the app:  uv run streamlit run app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
