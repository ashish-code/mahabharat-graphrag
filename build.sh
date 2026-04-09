#!/bin/bash
# Full build — all 8393 chunks (~45-60 min, complete Mahabharata)
PYTHONPATH=src uv run python -m mahabharat.build
