"""
knowledge_decomposer.py - Break a ContentChunk into granular KnowledgeAtoms.

Uses Claude to extract typed knowledge granules from raw content chunks.
Each atom is a single, self-contained knowledge statement.
"""
import json
import uuid
from datetime import datetime
from typing import List

import anthropic

from backend.config import ANTHROPIC_API_KEY, MODEL
from backend.models.schemas import KnowledgeAtom, KnowledgeAtomType, AtomStatus, ContentChunk

client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

DECOMPOSE_PROMPT = """אתה מומחה בניתוח ידע רפואי/מקצועי. המשימה שלך: פרק את קטע הטקסט לגרגרי ידע בסיסיים.

כל גרגר = יחידת מידע אחת, ספציפית, עצמאית — ניתנת לשימוש ללא הקשר נוסף.

סוגי גרגרים:
- concept: מושג או הגדרה מקצועית
- clinical_insight: תובנה קלינית, אבחנתית, או פתופיזיולוגית
- thinking_principle: עקרון חשיבה, מתודולוגיה, או תבנית הכרעה
- management_rule: כלל ניהולי, פרוטוקול, או המלצה מעשית
- medication: תרופה — שם, מינון, אינדיקציה, אזהרות
- pathogen: חיידק / נגיף / פרזיט — שם ומאפיינים
- approach: גישה טיפולית, אסטרטגיה, או עמדה מקצועית
- topic: נושא כללי בלבד (כשאין טיפוס מדויק יותר)
- other: אחר

טקסט לפירוק:
{text}

החזר JSON בלבד (ללא טקסט נוסף):
{{
  "atoms": [
    {{
      "content": "משפט אחד עד שלושה, ספציפי ועצמאי",
      "atom_type": "<סוג>",
      "tags": ["תג1", "תג2", "תג3"]
    }}
  ]
}}

כללים קשיחים:
- כל גרגר: 1-3 משפטים, ספציפי, עצמאי
- לא לחזור על מידע — גרגר אחד לכל יחידת ידע
- בין 3 ל-12 גרגרים לקטע
- בעברית בלבד
- tags: 2-4 מילות מפתח בעברית"""


async def decompose_chunk(chunk: ContentChunk) -> List[KnowledgeAtom]:
    """
    Call Claude to decompose a ContentChunk into granular KnowledgeAtoms.
    Returns empty list on failure (non-blocking).
    """
    try:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": DECOMPOSE_PROMPT.format(text=chunk.text[:3000]),
            }],
        )
        raw = response.content[0].text
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            return []
        data = json.loads(raw[start:end])
        atoms = []
        now = datetime.now().isoformat()
        for item in data.get("atoms", []):
            content = item.get("content", "").strip()
            if not content:
                continue
            atom_type_str = item.get("atom_type", "other")
            try:
                atom_type = KnowledgeAtomType(atom_type_str)
            except ValueError:
                atom_type = KnowledgeAtomType.OTHER
            atoms.append(KnowledgeAtom(
                id=str(uuid.uuid4()),
                content=content,
                atom_type=atom_type,
                tags=item.get("tags", []),
                source_chunks=[chunk.id],
                source_names=[chunk.source_name],
                confidence=1.0,
                status=AtomStatus.ACTIVE,
                created_at=now,
                updated_at=now,
                version=1,
            ))
        return atoms
    except Exception:
        return []
