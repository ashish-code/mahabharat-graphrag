import os
import boto3
from dotenv import load_dotenv

load_dotenv()

# AWS Bedrock configuration
AWS_PROFILE = os.getenv("AWS_PROFILE", "vscode-user")
AWS_REGION  = os.getenv("AWS_REGION", "us-east-1")

def get_bedrock_client():
    # If AWS_ACCESS_KEY_ID is set (e.g. Streamlit Cloud secrets), boto3 picks up
    # credentials from env vars automatically — don't pass profile_name or it
    # will fail on hosts that have no ~/.aws/config.
    if os.getenv("AWS_ACCESS_KEY_ID"):
        session = boto3.Session(region_name=os.getenv("AWS_DEFAULT_REGION", AWS_REGION))
    else:
        session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
    return session.client("bedrock-runtime")

# Models (Amazon Nova — available by default, no access request needed)
EXTRACTION_MODEL = os.getenv("EXTRACTION_MODEL", "amazon.nova-lite-v1:0")
ANSWER_MODEL     = os.getenv("ANSWER_MODEL",     "amazon.nova-pro-v1:0")

# Paths
PDF_PATH        = "data/pdf/Mahabharata.pdf"
DATA_DIR        = "data"
GRAPH_PATH      = "data/graph.json"
FAISS_INDEX_PATH = "data/faiss_index"

# Chunking
CHUNK_SIZE       = 2000
CHUNK_OVERLAP    = 200
EXTRACTION_BATCH = 5

# Graph RAG retrieval
TOP_K_VECTOR            = 5
TOP_K_GRAPH_HOPS        = 2
MAX_GRAPH_CONTEXT_NODES = 20

# Entity matching
FUZZY_MATCH_THRESHOLD = int(os.getenv("FUZZY_MATCH_THRESHOLD", "70"))

# Phase 2 – Hybrid Search
RRF_K          = int(os.getenv("RRF_K", "60"))
TOP_K_HYBRID   = int(os.getenv("TOP_K_HYBRID", "8"))
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
RERANKER_TOP_N = int(os.getenv("RERANKER_TOP_N", "5"))

# Phase 3 – Relationship Discovery
COMMUNITY_RESOLUTION = float(os.getenv("COMMUNITY_RESOLUTION", "1.0"))
MIN_CONFIDENCE       = os.getenv("MIN_CONFIDENCE", "low")
