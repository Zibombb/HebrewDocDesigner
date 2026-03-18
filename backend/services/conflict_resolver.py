"""
conflict_resolver.py - Living Knowledge Base logic.

For each new KnowledgeAtom, check against existing atoms and decide:
  ADD       - Novel knowledge, no similar atom exists
  REINFORCE - Same information from another source → confidence +0.1
  UPDATE    - More current/authoritative → supersede old atom
  CONFLICT  - Direct contradiction → flag both as CONFLICTED
  PARALLEL  - Different context/approach, both valid → mark as related
"""
import json
from datetime import datetime
from typing import Tuple

import anthropic

from backend.config import ANTHROPIC_API_KEY, MODEL
from backend.models.schemas import KnowledgeAtom, AtomStatus, AtomProcessingResult
from backend.services import atom_store

client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

# Similarity thresholds (cosine similarity, 0-1)
SIMILARITY_THRESHOLD = 0.87   # Below this → atoms are unrelated, just ADD
REINFORCE_THRESHOLD = 0.94    # Above this without conflict → likely same fact

RELATION_PROMPT = """השווה שני גרגרי ידע וקבע את הקשר ביניהם.

גרגר חדש:
{new}

גרגר קיים:
{existing}

אפשרויות:
- reinforce: אותו מידע / עובדה, ממקור אחר → מחזק את הקיים
- update: המידע החדש מעודכן יותר / מדויק יותר → יש לעדכן את הקיים
- conflict: סתירה ישירה — אחד מהם שגוי
- parallel: מידע שונה, תחום קרוב — שניהם תקפים בהקשרים שונים
- unrelated: לא קשורים כלל

החזר JSON בלבד:
{{"relation": "<reinforce|update|conflict|parallel|unrelated>", "reason": "הסבר קצר בעברית"}}"""


async def _classify_relation(new_content: str, existing_content: str) -> Tuple[str, str]:
    """Ask Claude to classify the relation between two atom contents."""
    try:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=256,
            messages=[{
                "role": "user",
                "content": RELATION_PROMPT.format(new=new_content, existing=existing_content),
            }],
        )
        raw = response.content[0].text
        data = json.loads(raw[raw.find("{"):raw.rfind("}") + 1])
        return data.get("relation", "unrelated"), data.get("reason", "")
    except Exception:
        return "unrelated", ""


async def process_new_atom(atom: KnowledgeAtom) -> AtomProcessingResult:
    """
    Determine the fate of a new KnowledgeAtom relative to existing knowledge.
    Mutates the store accordingly and returns a processing result.
    """
    similar = atom_store.find_similar(atom.content, n_results=3, threshold=SIMILARITY_THRESHOLD)
    now = datetime.now().isoformat()

    if not similar:
        atom_store.add_atom(atom)
        return AtomProcessingResult(
            action="ADD",
            atom_id=atom.id,
            message=f"גרגר ידע חדש נוסף [{atom.atom_type.value}]",
        )

    top = similar[0]
    existing_id = top["id"]

    # Fast path: very high similarity → almost certainly the same fact
    if top["similarity"] >= REINFORCE_THRESHOLD:
        relation = "reinforce"
        reason = "דמיון גבוה מאוד"
    else:
        relation, reason = await _classify_relation(atom.content, top["content"])

    # --- REINFORCE ---
    if relation == "reinforce":
        new_confidence = min(float(top["confidence"]) + 0.1, 2.0)
        existing_sources = top["source_names"]
        merged_sources = ", ".join(set(existing_sources) | set(atom.source_names))
        atom_store.update_atom_meta(
            existing_id,
            top["content"],
            {
                "confidence": str(round(new_confidence, 3)),
                "source_names": merged_sources,
                "updated_at": now,
            },
        )
        return AtomProcessingResult(
            action="REINFORCE",
            atom_id=existing_id,
            message=f"גרגר קיים חוזק (confidence: {new_confidence:.1f}) — {reason}",
        )

    # --- UPDATE ---
    if relation == "update":
        # Mark old as superseded
        atom_store.update_atom_meta(
            existing_id,
            top["content"],
            {"status": AtomStatus.SUPERSEDED.value, "superseded_by": atom.id, "updated_at": now},
        )
        # New atom inherits incremented version
        atom.version = int(top.get("version", 1)) + 1
        atom_store.add_atom(atom)
        return AtomProcessingResult(
            action="UPDATE",
            atom_id=atom.id,
            affected_atom_id=existing_id,
            message=f"גרגר עודכן לגרסה {atom.version} — {reason}",
        )

    # --- CONFLICT ---
    if relation == "conflict":
        # Flag existing
        existing_conflicts = top.get("conflicts_with", [])
        if atom.id not in existing_conflicts:
            existing_conflicts.append(atom.id)
        atom_store.update_atom_meta(
            existing_id,
            top["content"],
            {
                "status": AtomStatus.CONFLICTED.value,
                "conflicts_with": ", ".join(existing_conflicts),
                "updated_at": now,
            },
        )
        # Add new as conflicted too
        atom.status = AtomStatus.CONFLICTED
        atom.conflicts_with = [existing_id]
        atom_store.add_atom(atom)
        return AtomProcessingResult(
            action="CONFLICT",
            atom_id=atom.id,
            affected_atom_id=existing_id,
            message=f"סתירה זוהתה — {reason}",
        )

    # --- PARALLEL ---
    if relation == "parallel":
        atom.related_to = [existing_id]
        # Mark existing as related too
        existing_related = top.get("related_to", [])
        if atom.id not in existing_related:
            existing_related.append(atom.id)
        atom_store.update_atom_meta(
            existing_id,
            top["content"],
            {"related_to": ", ".join(existing_related), "updated_at": now},
        )
        atom_store.add_atom(atom)
        return AtomProcessingResult(
            action="PARALLEL",
            atom_id=atom.id,
            affected_atom_id=existing_id,
            message=f"גרגר מקביל — {reason}",
        )

    # --- UNRELATED / default → ADD ---
    atom_store.add_atom(atom)
    return AtomProcessingResult(
        action="ADD",
        atom_id=atom.id,
        message=f"גרגר ידע חדש נוסף [{atom.atom_type.value}]",
    )
