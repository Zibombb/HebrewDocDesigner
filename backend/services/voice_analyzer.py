import json
import anthropic
from typing import List, Optional
from backend.config import ANTHROPIC_API_KEY, MODEL, VOICE_PROFILE_PATH
from backend.models.schemas import VoiceProfile

client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

ANALYSIS_PROMPT = """אתה מומחה לניתוח סגנון כתיבה. נתח את דוגמאות הכתיבה הבאות וצור פרופיל קולי מפורט.

דוגמאות הכתיבה:
{samples}

נתח את הנקודות הבאות:
1. סגנון כתיבה: רשמי/לא-רשמי, ישיר/עשיר, אקדמי/שיחתי
2. מבנה משפטים: אורך ממוצע, מורכבות, קצב
3. מבנה פסקאות: אורך, מעברים בין רעיונות
4. אוצר מילים: עושר, שימוש בעברית לעומת מונחים מקצועיים
5. אמצעים רטוריים: מטפורות, אנלוגיות, חזרות
6. טון: חמים/קר, סמכותי/ענוותן, תשוקתי/אובייקטיבי
7. דפוסים ייחודיים: ביטויים, מבנים, הרגלי כתיבה
8. כיצד הכותב פותח נושאים
9. כיצד הכותב מסכם קטעים
10. כיצד הכותב מטפל בדוגמאות ומקרים

החזר JSON בדיוק בפורמט הבא (בלי הסברים נוספים):
{{
  "style_description": "תיאור נרטיבי מקיף של הקול - לפחות 200 מילים",
  "formality_level": <מספר 1-10>,
  "sentence_complexity": <מספר 1-10>,
  "vocabulary_richness": <מספר 1-10>,
  "tone_keywords": ["מילת מפתח 1", "מילת מפתח 2", "מילת מפתח 3", "מילת מפתח 4", "מילת מפתח 5"],
  "unique_phrases": ["ביטוי ייחודי 1", "ביטוי ייחודי 2", "ביטוי ייחודי 3"],
  "rhetorical_patterns": ["דפוס רטורי 1", "דפוס רטורי 2", "דפוס רטורי 3"],
  "writing_instruction": "הוראה מפורטת לכלי AI כיצד לכתוב בסגנון זה - לפחות 300 מילים. כלול: טון, סגנון, מבנה, אוצר מילים, דפוסים ייחודיים, כיצד לפתוח פסקאות, כיצד לסכם, כיצד להציג דוגמאות, שיטות הנמקה, ועוד."
}}"""


async def analyze_voice_samples(samples: List[str]) -> VoiceProfile:
    combined = "\n\n---\n\n".join(samples)

    async with client.messages.stream(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        messages=[{
            "role": "user",
            "content": ANALYSIS_PROMPT.format(samples=combined)
        }]
    ) as stream:
        response = await stream.get_final_message()

    # Extract text content
    text = next(b.text for b in response.content if b.type == "text")

    # Parse JSON
    start = text.find("{")
    end = text.rfind("}") + 1
    data = json.loads(text[start:end])
    data["sample_count"] = len(samples)

    profile = VoiceProfile(**data)
    save_voice_profile(profile)
    return profile


def save_voice_profile(profile: VoiceProfile):
    VOICE_PROFILE_PATH.write_text(
        profile.model_dump_json(indent=2), encoding="utf-8"
    )


def load_voice_profile() -> Optional[VoiceProfile]:
    if not VOICE_PROFILE_PATH.exists():
        return None
    data = json.loads(VOICE_PROFILE_PATH.read_text(encoding="utf-8"))
    return VoiceProfile(**data)
