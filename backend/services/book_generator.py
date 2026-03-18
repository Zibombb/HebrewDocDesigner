import json
import uuid
from datetime import datetime
from typing import AsyncGenerator, List, Optional

import anthropic
from backend.config import ANTHROPIC_API_KEY, MODEL, BOOKS_PATH
from backend.models.schemas import Book, BookChapter, VoiceProfile, CreateBookRequest
from backend.services import vector_store

client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

OUTLINE_PROMPT = """אתה עוזר ספרותי מומחה. עליך ליצור תוכן עניינים לספר על בסיס החומרים הקיימים.

פרטי הספר:
כותרת: {title}
תיאור: {description}
רעיונות ראשוניים לפרקים: {chapter_ideas}
מספר פרקים מבוקש: {n_chapters}

נושאים זמינים מהחומרים שנטענו:
{available_topics}

צור תוכן עניינים מלא. החזר JSON בדיוק בפורמט הבא:
{{
  "chapters": [
    {{
      "title": "כותרת הפרק",
      "description": "תיאור מה הפרק עוסק בו (2-3 משפטים)"
    }}
  ]
}}"""

CHAPTER_PROMPT = """אתה כותב ספרים מקצועי. כתוב פרק שלם לספר בסגנון הכתיבה של המחבר.

===הוראות סגנון הכתיבה===
{writing_instruction}

===פרטי הפרק===
כותרת הספר: {book_title}
פרק: {chapter_title}
תיאור הפרק: {chapter_description}

===חומרי מקור רלוונטיים===
{source_materials}

===הוראות===
- כתוב פרק שלם ועשיר בדיוק בסגנון הכתיבה המתואר לעיל
- השתמש בחומרי המקור כבסיס לתוכן
- הוסף מעומק, דוגמאות, ניתוחים - אך שמור על הסגנון האישי
- אורך הפרק: 800-1500 מילים
- כתוב ישירות את תוכן הפרק בלי כותרת "פרק" בתחילה
- הפרק צריך להרגיש כמו חלק אורגני מהספר"""


async def generate_book_outline(request: CreateBookRequest) -> Book:
    topics = vector_store.get_all_topics()
    topics_str = "\n".join(f"- {t}" for t in topics) if topics else "אין נושאים זמינים עדיין"

    response = await client.messages.create(
        model=MODEL,
        max_tokens=2048,
        thinking={"type": "adaptive"},
        messages=[{
            "role": "user",
            "content": OUTLINE_PROMPT.format(
                title=request.title,
                description=request.description,
                chapter_ideas=request.chapter_ideas or "לא סופקו",
                n_chapters=request.n_chapters,
                available_topics=topics_str,
            )
        }]
    )

    text = next(b.text for b in response.content if b.type == "text")
    start = text.find("{")
    end = text.rfind("}") + 1
    data = json.loads(text[start:end])

    now = datetime.now().isoformat()
    book_id = str(uuid.uuid4())
    chapters = [
        BookChapter(
            id=str(uuid.uuid4()),
            title=ch["title"],
            description=ch["description"],
            order=i,
            status="pending",
        )
        for i, ch in enumerate(data["chapters"])
    ]

    book = Book(
        id=book_id,
        title=request.title,
        description=request.description,
        chapters=chapters,
        created_at=now,
        updated_at=now,
    )
    save_book(book)
    return book


async def generate_chapter_stream(
    book: Book,
    chapter: BookChapter,
    voice_profile: Optional[VoiceProfile],
) -> AsyncGenerator[str, None]:
    # Retrieve relevant content
    query = f"{book.title} {chapter.title} {chapter.description}"
    results = vector_store.search(query, n_results=8)

    if results:
        materials = "\n\n---\n\n".join(
            f"נושא: {r.topic}\n{r.text}" for r in results
        )
    else:
        materials = "אין חומרי מקור ספציפיים - כתוב מידע כללי בנושא"

    writing_instruction = (
        voice_profile.writing_instruction
        if voice_profile
        else "כתוב בסגנון עברי מקצועי, ברור ומעניין. השתמש בשפה עשירה ובדוגמאות."
    )

    async with client.messages.stream(
        model=MODEL,
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": CHAPTER_PROMPT.format(
                writing_instruction=writing_instruction,
                book_title=book.title,
                chapter_title=chapter.title,
                chapter_description=chapter.description,
                source_materials=materials,
            )
        }]
    ) as stream:
        async for text in stream.text_stream:
            yield text


def load_books() -> List[Book]:
    if not BOOKS_PATH.exists():
        return []
    data = json.loads(BOOKS_PATH.read_text(encoding="utf-8"))
    return [Book(**b) for b in data]


def load_book(book_id: str) -> Optional[Book]:
    return next((b for b in load_books() if b.id == book_id), None)


def save_book(book: Book):
    books = load_books()
    books = [b for b in books if b.id != book.id]
    books.append(book)
    BOOKS_PATH.write_text(
        json.dumps([b.model_dump() for b in books], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def update_chapter_content(book_id: str, chapter_id: str, content: str) -> Optional[Book]:
    book = load_book(book_id)
    if not book:
        return None
    for ch in book.chapters:
        if ch.id == chapter_id:
            ch.content = content
            ch.status = "done"
            break
    book.updated_at = datetime.now().isoformat()
    save_book(book)
    return book


def delete_book(book_id: str):
    books = [b for b in load_books() if b.id != book_id]
    BOOKS_PATH.write_text(
        json.dumps([b.model_dump() for b in books], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
