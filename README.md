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
  Claude Agent  ──── decides ────►  graph_lookup tool   ──► NetworkX graph traversal
      │                                                       (entities + typed relations)
      │          ──── decides ────►  passage_search tool ──► FAISS vector search
      │                                                       (source text passages)
      ▼
 Synthesized Answer  +  Interactive Graph Visualization
```

### Two-Tool Architecture

| Tool | When Used | Returns |
|---|---|---|
| `graph_lookup` | Who/what/how-related questions | Entities + typed relationships from knowledge graph |
| `passage_search` | Why/how/narrative questions | Relevant passages from the Mahabharata text |

---

## Features

- **Pre-seeded knowledge graph** — 53 hand-verified entities and 90 typed relationships covering the full Kuru lineage, Pandavas, Kauravas, key teachers, places, and events — works immediately without any build
- **LLM-enriched graph** — Claude Haiku extracts additional entities and relationships from the source PDF, augmenting the seed graph
- **Interactive graph visualization** — pyvis-rendered subgraph showing exactly which nodes and edges informed each answer
- **Knowledge Graph Explorer tab** — browse the full character graph, search by entity, adjust traversal depth
- **Conversation memory** — multi-turn chat with rolling 4-turn history
- **Tool call transparency** — UI badges show whether the agent used graph traversal, passage search, or both

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM (answers) | Claude Sonnet (`claude-sonnet-4-6`) via Anthropic API |
| LLM (extraction) | Claude Haiku (`claude-haiku-4-5-20251001`) — fast, cost-efficient |
| Agent framework | Anthropic tool-use API (two tools: `graph_lookup`, `passage_search`) |
| Knowledge graph | NetworkX (in-memory, persisted to JSON) |
| Vector store | FAISS + `all-MiniLM-L6-v2` embeddings (runs locally, no API cost) |
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
# Edit .env and add your Anthropic API key
```

```env
ANTHROPIC_API_KEY=sk-ant-...
```

Get a key at [console.anthropic.com](https://console.anthropic.com/).

### 3. Add the source PDF

Place your Mahabharata PDF at:

```
data/pdf/Mahabharata.pdf
```

### 4. Build the index

Choose a build size based on available time. The app is usable immediately (seed graph is always present); larger builds enrich the graph with LLM-extracted relationships.

| Script | Chunks | Time | API Cost | Coverage |
|---|---|---|---|---|
| `./build_fast.sh` | 200 | ~5 min | ~$0.10 | Books 1–2 |
| `./build_medium.sh` | 600 | ~15 min | ~$0.30 | Books 1–4 (recommended) |
| `./build.sh` | 8393 | ~45–60 min | ~$5 | Full Mahabharata |

```bash
./build_medium.sh
```

The pipeline:
1. Extracts text from the PDF (PyMuPDF)
2. Builds a FAISS vector index with local embeddings — **no API cost**
3. Runs Claude Haiku over text chunks to extract additional entities and relationships
4. Merges extracted data with the pre-seeded character graph
5. Saves `data/graph.json` and `data/faiss_index/` — graph is checkpointed every ~100 chunks, so `Ctrl+C` preserves all progress

### 5. Run the app

```bash
uv run streamlit run app.py
```

---

## Project Structure

```
mahabharat-graphrag/
├── app.py                          # Streamlit frontend (chat + graph explorer)
├── build_fast.sh                   # 200 chunks, ~5 min
├── build_medium.sh                 # 600 chunks, ~15 min (recommended)
├── build.sh                        # All 8393 chunks, ~60 min
├── data/
│   └── pdf/
│       └── Mahabharata.pdf         # Source document (not included in repo)
└── src/mahabharat/
    ├── config.py                   # Models, paths, chunking parameters
    ├── seed_data.py                # Pre-verified 53 entities + 90 relationships
    ├── ingest.py                   # PDF → sliding-window text chunks (PyMuPDF)
    ├── extractor.py                # LLM entity/relationship extraction (Haiku)
    ├── graph.py                    # NetworkX graph: build, save, load, BFS traversal
    ├── vector_store.py             # FAISS index build/load + similarity search
    ├── agent.py                    # Two-tool Claude agent
    ├── visualize.py                # pyvis graph → HTML for Streamlit
    └── build.py                    # Offline build pipeline (incremental saves)
```

---

## Configuration

Key parameters in `src/mahabharat/config.py`:

| Parameter | Default | Description |
|---|---|---|
| `EXTRACTION_MODEL` | `claude-haiku-4-5-20251001` | Model for entity/relation extraction |
| `ANSWER_MODEL` | `claude-sonnet-4-6` | Model for final answer synthesis |
| `CHUNK_SIZE` | `2000` | Characters per text chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between adjacent chunks |
| `EXTRACTION_BATCH` | `5` | Chunks processed per LLM call |
| `TOP_K_VECTOR` | `5` | Passages returned per vector query |
| `TOP_K_GRAPH_HOPS` | `2` | BFS traversal depth from seed nodes |
| `MAX_GRAPH_CONTEXT_NODES` | `20` | Max graph nodes passed to LLM context |

---

## Example Questions

**Relationship questions** (uses `graph_lookup`):
- *What is the relationship between Karna and the Pandavas?*
- *Describe the family tree of the Kauravas.*
- *Who were the teachers of Arjuna?*
- *How is Draupadi related to Drupada and Dhrishtadyumna?*

**Narrative questions** (uses `passage_search`):
- *Why did Bhishma take a vow of celibacy?*
- *What role did Krishna play in the Kurukshetra war?*
- *Who killed Drona and how was he tricked?*

**Complex questions** (uses both tools):
- *Who killed Abhimanyu and why couldn't he escape the Chakravyuha?*
- *Why is Karna considered a tragic hero?*

---

## How Graph RAG Works Here

1. **Query** — user asks a question in the chat UI
2. **Agent** — Claude (`claude-sonnet-4-6`) chooses which tool(s) to call based on the question type
3. **Graph traversal** (`graph_lookup`) — named entities are matched to graph nodes; BFS expands 2 hops to collect the surrounding subgraph of entities and typed relationships
4. **Passage retrieval** (`passage_search`) — FAISS cosine similarity finds the top-5 most relevant source passages
5. **Synthesis** — Claude generates a grounded answer from the combined graph + passage context
6. **Visualization** — the subgraph consulted during the answer is rendered as an interactive pyvis graph in the UI

---

## License

MIT
