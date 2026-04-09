#!/bin/bash
# Medium build — first 600 chunks (~15 min, Books 1-4 of Mahabharata)
# Covers: full lineage, dice game, forest exile, key battles & characters
# Recommended for demos and interviews
CHUNK_LIMIT=600 uv run python -m mahabharat.build
