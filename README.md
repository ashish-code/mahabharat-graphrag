# Mahabharat Graph RAG Chatbot

A knowledge-graph-powered question-answering system for the Mahabharata epic, built with **Graph RAG** (Retrieval-Augmented Generation). Ask complex questions about characters, family trees, alliances, battles, and events — and get answers grounded in both structured relationship data and source text passages.

![Python](https://img.shields.io/badge/python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/streamlit-1.56-red?logo=streamlit)
![LangChain](https://img.shields.io/badge/langchain-latest-green)
![Claude](https://img.shields.io/badge/Claude-claude--sonnet--4--6-orange?logo=anthropic)

---

## What is Graph RAG?

Standard RAG retrieves text passages by vector similarity. **Graph RAG** adds a structured knowledge graph layer, enabling the system to:

- Answer relationship questions precisely (`Who is Karna's biological mother?`) by traversing typed edges in a graph
- Answer narrative questions contextually (`Why did the Kurukshetra war start?`) via semantic passage search
- Combine both when needed — the agent decides at query time

```
User Question
      │
      ▼
  Claude Agent  ──── decides ────►  graph_lookup tool   ──► NetworkX traversal
      │                                                       (entities + relations)
      │          ──── decides ────►  passage_search tool ──► FAISS vector search
      │                                                       (source text passages)
      ▼
 Synthesized Answer  +  Graph Visualization
```

### Two-Tool Architecture

| Tool | When Used | Returns |
|---|---|---|
| `graph_lookup` | Who/what/how-related questions | Entities + typed relationships from knowledge graph |
| `passage_search` | Why/how/narrative questions | Relevant passages from the Mahabharata text |

---

## Features

- **Pre-seeded knowledge graph** — 53 hand-verified entities and 90 typed relationships covering the full Kuru lineage, Pandavas, Kauravas, key teachers, weapons, places, and events
- **LLM-enriched graph** — entity and relationship extraction via Claude Haiku over the full 2328-page PDF augments the seed graph
- **Interactive graph visualization** — pyvis-rendered subgraph showing exactly which nodes and edges informed each answer
- **Knowledge Graph Explorer tab** — browse the full character graph, search by entity, adjust depth
- **Conversation memory** — multi-turn chat with 4-turn rolling history
- **Tool call transparency** — UI badges show whether the agent used graph traversal, passage search, or both

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM (answers) | Claude Sonnet (`claude-sonnet-4-6`) via Anthropic API |
| LLM (extraction) | Claude Haiku (`claude-haiku-4-5-20251001`) — fast, cost-efficient |
| Agent framework | Anthropic tool-use API (two tools: `graph_lookup`, `passage_search`) |
| Knowledge graph | NetworkX (in-memory, persisted to JSON) |
| Vector store | FAISS with `all-MiniLM-L6-v2` embeddings (local, no API cost) |
| PDF extraction | PyMuPDF |
| Frontend | Streamlit |
| Graph visualization | pyvis |
| Package manager | uv |

---

## Quickstart

### 1. Clone and install

```bash
git clone https://github.com/ashish-code/mahabharat-graphrag.git
cd mahabharat-graphrag
uv sync
```

### 2. Configure

```bash
cp .env.example .env
# Add your Anthropic API key to .env
```

```env
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Add the source PDF

Place your Mahabharata PDF at:

```
data/pdf/Mahabharata.pdf
```

### 4. Build the index

**Fast build** (~5 min, 200 chunks, good for demos):

```bash
./build_fast.sh
```

**Full build** (~45–60 min, all 8393 chunks):

```bash
./build.sh
```

The build pipeline:
1. Extracts text from the PDF (PyMuPDF)
2. Builds a FAISS vector index with local embeddings (no API cost)
3. Runs Claude Haiku over text chunks to extract entities and relationships
4. Merges extracted data with the pre-seeded character graph
5. Saves `data/graph.json` and `data/faiss_index/`

> **Tip:** The app works immediately after a fast build — seed graph data is available from the first run.

### 5. Run the app

```bash
uv run streamlit run app.py
```

---

## Project Structure

```
mahabharat-graphrag/
├── app.py                          # Streamlit frontend (chat + graph explorer)
├── build_fast.sh                   # Fast build (200 chunks, ~5 min)
├── build.sh                        # Full build (all chunks)
├── data/
│   └── pdf/
│       └── Mahabharata.pdf         # Source document (not included in repo)
└── src/mahabharat/
    ├── config.py                   # Models, paths, chunking parameters
    ├── seed_data.py                # Pre-verified 53 entities + 90 relationships
    ├── ingest.py                   # PDF → text chunks (PyMuPDF)
    ├── extractor.py                # LLM entity/relationship extraction
    ├── graph.py                    # NetworkX graph build, save, load, BFS traversal
    ├── vector_store.py             # FAISS index build/load + similarity search
    ├── agent.py                    # Two-tool Claude agent (graph_lookup + passage_search)
    ├── visualize.py                # pyvis graph rendering for Streamlit
    └── build.py                    # Offline build pipeline
```

---

## Configuration

Key parameters in `src/mahabharat/config.py`:

| Parameter | Default | Description |
|---|---|---|
| `EXTRACTION_MODEL` | `claude-haiku-4-5-20251001` | Model for entity extraction |
| `ANSWER_MODEL` | `claude-sonnet-4-6` | Model for final answers |
| `CHUNK_SIZE` | `2000` | Characters per text chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `EXTRACTION_BATCH` | `5` | Chunks per LLM extraction call |
| `TOP_K_VECTOR` | `5` | Passages retrieved per query |
| `TOP_K_GRAPH_HOPS` | `2` | Graph traversal depth |
| `MAX_GRAPH_CONTEXT_NODES` | `20` | Max nodes included in LLM context |

---

## Example Questions

- *What is the relationship between Karna and the Pandavas?*
- *Describe the family tree of the Kauravas.*
- *Who killed Abhimanyu and how did it happen?*
- *What role did Krishna play in the Kurukshetra war?*
- *Why did Bhishma take a vow of celibacy, and how did it affect the throne?*
- *Who were the teachers of Arjuna?*
- *How is Draupadi related to Drupada and Dhrishtadyumna?*
- *Who killed Drona and how was he tricked?*

---

## How Graph RAG Works Here

1. **Query** — user asks a question
2. **Agent** — Claude decides which tool(s) to invoke based on the question type
3. **Graph traversal** (`graph_lookup`) — named entities are matched to graph nodes; BFS expands 2 hops to collect relevant entities and typed relationships
4. **Passage retrieval** (`passage_search`) — FAISS cosine similarity finds the most relevant source text passages
5. **Synthesis** — Claude generates a grounded answer from the combined graph + passage context
6. **Visualization** — the subgraph used in the answer is rendered interactively in the UI

---

## License

MIT
