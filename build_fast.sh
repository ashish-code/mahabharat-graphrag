#!/bin/bash
# Fast build — first 200 chunks (~5-8 min, covers Book 1 of Mahabharata)
# Good enough for demo: includes Pandavas, Kauravas, key characters & relationships
CHUNK_LIMIT=200 uv run python -m mahabharat.build
