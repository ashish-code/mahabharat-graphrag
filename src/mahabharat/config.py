import os
import boto3
from dotenv import load_dotenv

load_dotenv()

# AWS Bedrock configuration
AWS_PROFILE = os.getenv("AWS_PROFILE", "vscode-user")
AWS_REGION  = os.getenv("AWS_REGION", "us-east-1")

def get_bedrock_client():
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
