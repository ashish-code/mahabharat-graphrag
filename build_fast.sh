#!/bin/bash
# Fast build — first 200 chunks (~5 min, Books 1-2 of Mahabharata)
# Covers: core lineage, Pandavas/Kauravas, Drona, early stories
CHUNK_LIMIT=200 uv run python -m mahabharat.build
