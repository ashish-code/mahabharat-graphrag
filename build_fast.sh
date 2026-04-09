#!/bin/bash
# Fast build — first 200 chunks (~5 min, Books 1–2 of Mahabharata)
CHUNK_LIMIT=200 PYTHONPATH=src uv run python -m mahabharat.build
