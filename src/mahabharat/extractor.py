"""Entity and relationship extraction using AWS Bedrock (converse API)."""
import json
import re
from typing import List, Dict, Tuple
from .config import get_bedrock_client, EXTRACTION_MODEL, EXTRACTION_BATCH

ENTITY_RELATION_PROMPT = """\
You are analyzing passages from the Mahabharata epic. Extract entities and relationships.

PASSAGE:
{text}

Extract:
1. ENTITIES: Characters, places, weapons, clans, kingdoms mentioned.
2. RELATIONSHIPS: Directional relationships between entities.

Respond ONLY with valid JSON in this exact format:
{{
  "entities": [
    {{"name": "Arjuna", "type": "character", "description": "Pandava prince, skilled archer"}},
    {{"name": "Hastinapura", "type": "place", "description": "Capital of Kuru kingdom"}}
  ],
  "relationships": [
    {{"source": "Arjuna", "relation": "IS_BROTHER_OF", "target": "Bhima", "context": "Both are Pandava brothers"}},
    {{"source": "Arjuna", "relation": "FOUGHT_AT", "target": "Kurukshetra", "context": "Battle of Kurukshetra"}}
  ]
}}

Entity types: character, place, weapon, clan, kingdom, concept, event
Relation types: IS_BROTHER_OF, IS_FATHER_OF, IS_MOTHER_OF, IS_SON_OF, IS_WIFE_OF, IS_HUSBAND_OF,
  IS_ALLY_OF, IS_ENEMY_OF, IS_DISCIPLE_OF, IS_TEACHER_OF, RULES_OVER, FOUGHT_AT, FOUGHT_WITH,
  FOUGHT_AGAINST, OWNS, KILLED, WAS_KILLED_BY, PARTICIPATED_IN, BELONGS_TO, IS_INCARNATION_OF

Be precise. Only extract what is clearly stated or strongly implied in the passage.
Normalize entity names (use the most common English spelling).
"""


def extract_batch(chunks: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Extract entities and relations from a batch of chunks via Bedrock converse."""
    combined_text = "\n\n---\n\n".join(c["text"] for c in chunks)
    combined_text = combined_text[:6000]

    client = get_bedrock_client()
    try:
        response = client.converse(
            modelId=EXTRACTION_MODEL,
            messages=[{
                "role": "user",
                "content": [{"text": ENTITY_RELATION_PROMPT.format(text=combined_text)}],
            }],
            inferenceConfig={"maxTokens": 4096, "temperature": 0},
        )
        raw = response["output"]["message"]["content"][0]["text"].strip()

        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return data.get("entities", []), data.get("relationships", [])
    except Exception as e:
        print(f"  Extraction error: {e}")

    return [], []


def extract_all(chunks: List[Dict], progress_callback=None) -> Tuple[List[Dict], List[Dict]]:
    """Run extraction over all chunks in batches."""
    all_entities, all_relations = [], []
    batches = [chunks[i:i + EXTRACTION_BATCH] for i in range(0, len(chunks), EXTRACTION_BATCH)]
    total = len(batches)

    for i, batch in enumerate(batches):
        if progress_callback:
            progress_callback(i, total)
        else:
            print(f"  Extracting batch {i+1}/{total}...")
        entities, relations = extract_batch(batch)
        all_entities.extend(entities)
        all_relations.extend(relations)

    return all_entities, all_relations
