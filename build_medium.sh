#!/bin/bash
# Medium build — first 600 chunks (~15 min, Books 1–4 of Mahabharata)
# Recommended for demos and interviews
CHUNK_LIMIT=600 PYTHONPATH=src uv run python -m mahabharat.build
