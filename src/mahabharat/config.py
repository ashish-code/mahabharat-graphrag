import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Paths
PDF_PATH = "data/pdf/Mahabharata.pdf"
DATA_DIR = "data"
GRAPH_PATH = "data/graph.json"
FAISS_INDEX_PATH = "data/faiss_index"

# Extraction model (fast + cheap for bulk extraction)
EXTRACTION_MODEL = "claude-haiku-4-5-20251001"
# Answer model (smart for final answers)
ANSWER_MODEL = "claude-sonnet-4-6"

# Chunking
CHUNK_SIZE = 2000       # characters per chunk
CHUNK_OVERLAP = 200
EXTRACTION_BATCH = 5    # chunks per LLM extraction call

# Graph RAG retrieval
TOP_K_VECTOR = 5        # passages from FAISS
TOP_K_GRAPH_HOPS = 2    # graph traversal depth
MAX_GRAPH_CONTEXT_NODES = 20
