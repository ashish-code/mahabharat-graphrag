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
1. ENTITIES: Characters, places, weapons, clans, kingdoms, events, and concepts mentioned.
2. RELATIONSHIPS: Directional relationships between entities.

Respond ONLY with valid JSON in this exact format:
{{
  "entities": [
    {{"name": "Arjuna", "type": "character", "description": "Pandava prince, skilled archer"}},
    {{"name": "Hastinapura", "type": "place", "description": "Capital of Kuru kingdom"}}
  ],
  "relationships": [
    {{"source": "Arjuna", "relation": "IS_BROTHER_OF", "target": "Bhima", "context": "Both are Pandava brothers", "confidence": "high"}},
    {{"source": "Drona", "relation": "CURSED_BY", "target": "Parashurama", "context": "Cursed when Drona's true identity was revealed", "confidence": "medium"}}
  ]
}}

Entity types: character, place, weapon, clan, kingdom, concept, event

Relation types (use ONLY these):
  Family:     IS_BROTHER_OF, IS_SISTER_OF, IS_FATHER_OF, IS_MOTHER_OF, IS_SON_OF,
              IS_DAUGHTER_OF, IS_HUSBAND_OF, IS_WIFE_OF, IS_UNCLE_OF, IS_NEPHEW_OF,
              IS_AUNT_OF, IS_NIECE_OF, IS_COUSIN_OF, IS_GRANDSON_OF, IS_GRANDFATHER_OF
  Social:     IS_ALLY_OF, IS_ENEMY_OF, IS_TEACHER_OF, IS_DISCIPLE_OF, BETRAYED, PROTECTED
  Political:  RULES_OVER, BELONGS_TO, EXILED_BY
  Combat:     FOUGHT_AT, FOUGHT_WITH, FOUGHT_AGAINST, KILLED, WAS_KILLED_BY, VOWED_TO_KILL
  Spiritual:  CURSED_BY, BLESSED_BY, GRANTED_BOON_BY, BORN_FROM,
              IS_INCARNATION_OF, IS_REINCARNATION_OF
  Other:      OWNS, PARTICIPATED_IN

Confidence field (required for every relationship):
  "high"   — explicitly stated in the passage
  "medium" — clearly implied or strongly suggested
  "low"    — inferred from context, not directly stated

Rules:
- Use the most common English spelling for names (e.g. Arjuna not Arjun, Yudhishthira not Yudhisthir).
- Only extract what is present in this passage; do not use outside knowledge.
- Every relationship must have source, relation, target, context, and confidence.
"""


def extract_batch(chunks: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Extract entities and relations from a batch of chunks via Bedrock converse."""
    combined_text = "\n\n---\n\n".join(c["text"] for c in chunks)
    combined_text = combined_text[:8000]

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
