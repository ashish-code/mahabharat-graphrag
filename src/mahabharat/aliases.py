"""
Canonical alias map for Mahabharata characters.

Maps every known epithet, nickname, and alternate spelling to the canonical
node name used in the knowledge graph (matching seed_data.py exactly).

Usage:
    from .aliases import resolve_alias, resolve_aliases
"""
from typing import Dict, List

ALIASES: Dict[str, str] = {
    # ── Arjuna ────────────────────────────────────────────────────────────────
    "partha":       "Arjuna",   # son of Pritha (Kunti)
    "dhananjaya":   "Arjuna",   # winner of wealth
    "kiriti":       "Arjuna",   # crowned one
    "savyasachi":   "Arjuna",   # ambidextrous archer
    "gudakesha":    "Arjuna",   # thick-haired / conqueror of sleep
    "phalguna":     "Arjuna",   # born under Phalguna star
    "vijaya":       "Arjuna",   # victorious
    "jishnu":       "Arjuna",   # triumphant
    "bibhatsu":     "Arjuna",   # one who acts with disgust (for cruelty)
    "kapidhwaja":   "Arjuna",   # monkey-bannered (Hanuman on his chariot)
    "shvetavahana": "Arjuna",   # one with white horses

    # ── Krishna ───────────────────────────────────────────────────────────────
    "vasudeva":     "Krishna",  # son of Vasudeva
    "govinda":      "Krishna",  # protector of cows
    "madhava":      "Krishna",  # descendant of Madhu
    "keshava":      "Krishna",  # long-haired / slayer of Keshi
    "hrishikesha":  "Krishna",  # lord of the senses
    "janardana":    "Krishna",  # one who excites men
    "murari":       "Krishna",  # enemy of Mura
    "achyuta":      "Krishna",  # infallible one
    "damodara":     "Krishna",  # bound with a rope around the waist
    "madhusudana":  "Krishna",  # slayer of Madhu
    "hari":         "Krishna",  # the remover (of sins)
    "vāsudeva":     "Krishna",  # variant diacritic spelling

    # ── Bhima ─────────────────────────────────────────────────────────────────
    "vrikodara":    "Bhima",    # wolf-bellied
    "bhimasena":    "Bhima",    # full name
    "vayuputra":    "Bhima",    # son of Vayu
    "pavanaputra":  "Bhima",    # son of the wind god
    "bhimsena":     "Bhima",    # common spelling variant

    # ── Yudhishthira ──────────────────────────────────────────────────────────
    "dharmaraja":   "Yudhishthira",  # king of dharma
    "ajatashatru":  "Yudhishthira",  # one without enemies
    "dharmaputra":  "Yudhishthira",  # son of Dharma
    "yudhisthira":  "Yudhishthira",  # common spelling variant
    "yudhistir":    "Yudhishthira",  # common informal variant

    # ── Karna ─────────────────────────────────────────────────────────────────
    "radheya":      "Karna",    # son of Radha (foster mother)
    "vasusena":     "Karna",    # born with wealth (armour & earrings)
    "vrisha":       "Karna",    # virtuous / bull
    "sutaputra":    "Karna",    # son of a charioteer
    "vaikartana":   "Karna",    # one who cut off his armour
    "angaraja":     "Karna",    # king of Anga
    "anga-raja":    "Karna",    # hyphenated variant

    # ── Duryodhana ────────────────────────────────────────────────────────────
    "suyodhana":    "Duryodhana",   # good fighter (his preferred name)

    # ── Bhishma ───────────────────────────────────────────────────────────────
    "devavrata":    "Bhishma",  # birth name
    "gangaputra":   "Bhishma",  # son of Ganga
    "pitamaha":     "Bhishma",  # grandsire
    "gangeya":      "Bhishma",  # son of Ganga (variant)

    # ── Draupadi ──────────────────────────────────────────────────────────────
    "panchali":     "Draupadi", # princess of Panchala
    "krishnaa":     "Draupadi", # dark-complexioned one (feminine of Krishna)
    "yajnaseni":    "Draupadi", # born of the sacrificial fire
    "nityayuvvani": "Draupadi", # eternally youthful

    # ── Kunti ─────────────────────────────────────────────────────────────────
    "pritha":       "Kunti",    # birth name

    # ── Nakula ────────────────────────────────────────────────────────────────
    "nakul":        "Nakula",   # common shortened form

    # ── Sahadeva ──────────────────────────────────────────────────────────────
    "sahdev":       "Sahadeva", # common shortened form

    # ── Vyasa ─────────────────────────────────────────────────────────────────
    "veda vyasa":           "Vyasa",
    "krishna dvaipayana":   "Vyasa",
    "krishnadwaipayana":    "Vyasa",
    "dvaipayana":           "Vyasa",

    # ── Abhimanyu ─────────────────────────────────────────────────────────────
    "saubhadra":    "Abhimanyu",  # son of Subhadra

    # ── Drona ─────────────────────────────────────────────────────────────────
    "dronacharya":  "Drona",    # with honorific
    "acharya drona": "Drona",

    # ── Drupada ───────────────────────────────────────────────────────────────
    "yajnasena":    "Drupada",  # alternate name

    # ── Ashwatthama ───────────────────────────────────────────────────────────
    "ashvatthama":  "Ashwatthama",  # common spelling variant
    "ashwatthaman": "Ashwatthama",

    # ── Dhrishtadyumna ────────────────────────────────────────────────────────
    "dhristadyumna":    "Dhrishtadyumna",  # common spelling variant
    "dhrishtadyumna":   "Dhrishtadyumna",  # alternate spelling

    # ── Shalya ────────────────────────────────────────────────────────────────
    "salya":        "Shalya",   # common spelling variant

    # ── Shakuni ───────────────────────────────────────────────────────────────
    "soubala":      "Shakuni",  # son of Subala
    "saubala":      "Shakuni",

    # ── Ghatotkacha ───────────────────────────────────────────────────────────
    "ghatotkacha":  "Ghatotkacha",  # ensure consistent casing
    "ghatatkacha":  "Ghatotkacha",

    # ── Shikhandi ─────────────────────────────────────────────────────────────
    "shikhandini":  "Shikhandi",    # original female form name

    # ── Parikshit ─────────────────────────────────────────────────────────────
    "pariksit":     "Parikshit",    # common spelling variant

    # ── Vidura ────────────────────────────────────────────────────────────────
    "kshattri":     "Vidura",       # epithet meaning one born of mixed union
}


def resolve_alias(name: str) -> str:
    """Return canonical graph node name if alias found, else return name unchanged."""
    return ALIASES.get(name.lower().strip(), name)


def resolve_aliases(names: List[str]) -> List[str]:
    """
    Resolve a list of names through the alias table.

    For each name:
    - If an alias mapping exists, include only the canonical name.
      (The original is dropped — it might fuzzy-match the wrong node.)
    - If no alias mapping exists, include the original for downstream
      exact/fuzzy matching.
    Returns a deduplicated list preserving first-seen order.
    """
    resolved = []
    for name in names:
        canonical = resolve_alias(name)
        resolved.append(canonical)
        # Only keep the original if it did NOT resolve through the alias table,
        # so it can participate in fuzzy matching as a fallback.
        if canonical == name:
            pass  # original already added above
        # If resolved to a different canonical, do NOT add the original —
        # it could fuzzy-match an unrelated node (e.g. "Radheya" → "Radha").

    # Deduplicate preserving order
    seen: set = set()
    out: List[str] = []
    for n in resolved:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out
