"""Lightweight entity extractor for query-time named entity recognition."""
import json
import re
from typing import List
from .config import get_bedrock_client, EXTRACTION_MODEL

ENTITY_EXTRACT_PROMPT = """\
Extract all character names, place names, and event names from this question about the Mahabharata.
Return ONLY a JSON array of strings. Example: ["Arjuna", "Kurukshetra", "Drona"]

Question: {question}
"""


def extract_query_entities(question: str) -> List[str]:
    client = get_bedrock_client()
    try:
        response = client.converse(
            modelId=EXTRACTION_MODEL,
            messages=[{
                "role": "user",
                "content": [{"text": ENTITY_EXTRACT_PROMPT.format(question=question)}],
            }],
            inferenceConfig={"maxTokens": 256, "temperature": 0},
        )
        raw = response["output"]["message"]["content"][0]["text"].strip()
        match = re.search(r'\[.*?\]', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"Entity extraction error: {e}")
    return []
