import json
import uuid
import re
from datetime import datetime
from typing import List, Tuple
from pathlib import Path

import anthropic
from backend.config import ANTHROPIC_API_KEY, MODEL, CONTENT_SOURCES_PATH, MAX_CHUNK_SIZE
from backend.models.schemas import ContentChunk, ContentSource
from backend.services import vector_store
from backend.services.knowledge_decomposer import decompose_chunk
from backend.services.conflict_resolver import process_new_atom

client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

CHUNK_ANALYSIS_PROMPT = """נתח את קטע הטקסט הבא וחלץ מידע מובנה.

טקסט:
{text}

החזר JSON בדיוק בפורמט הבא (בלי הסברים נוספים):
{{
  "topic": "נושא מרכזי של הקטע (4-8 מילים)",
  "concepts": ["מושג 1", "מושג 2", "מושג 3"],
  "chunk_type": "<אחד מהבאים: definition/example/analysis/narrative/argument>"
}}"""


def extract_text_from_pdf(content: bytes) -> str:
    import fitz  # PyMuPDF
    doc = fitz.open(stream=content, filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n\n".join(pages)


def extract_text_from_docx(content: bytes) -> str:
    import io
    from docx import Document
    doc = Document(io.BytesIO(content))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def extract_text_from_txt(content: bytes) -> str:
    import chardet
    detected = chardet.detect(content)
    encoding = detected.get("encoding") or "utf-8"
    return content.decode(encoding, errors="replace")


def extract_text(filename: str, content: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(content)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(content)
    else:
        return extract_text_from_txt(content)


def split_into_chunks(text: str, max_words: int = MAX_CHUNK_SIZE) -> List[str]:
    """Split text into chunks by paragraphs, targeting max_words per chunk."""
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    chunks = []
    current_chunk = []
    current_words = 0

    for para in paragraphs:
        word_count = len(para.split())
        if current_words + word_count > max_words and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_words = word_count
        else:
            current_chunk.append(para)
            current_words += word_count

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


async def analyze_chunk(text: str) -> Tuple[str, List[str], str]:
    """Use Claude to extract topic, concepts, and type from a chunk."""
    try:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": CHUNK_ANALYSIS_PROMPT.format(text=text[:2000])
            }]
        )
        raw = response.content[0].text
        start = raw.find("{")
        end = raw.rfind("}") + 1
        data = json.loads(raw[start:end])
        return data.get("topic", "כללי"), data.get("concepts", []), data.get("chunk_type", "narrative")
    except Exception:
        return "כללי", [], "narrative"


async def process_file(filename: str, content: bytes) -> ContentSource:
    """Extract text, chunk it, analyze each chunk, and store in vector store."""
    text = extract_text(filename, content)
    chunks_text = split_into_chunks(text)

    source_id = str(uuid.uuid4())
    source_name = Path(filename).stem
    all_chunks = []
    all_topics = set()

    for i, chunk_text in enumerate(chunks_text):
        if not chunk_text.strip():
            continue
        topic, concepts, chunk_type = await analyze_chunk(chunk_text)
        all_topics.add(topic)
        chunk = ContentChunk(
            id=f"{source_id}_{i}",
            text=chunk_text,
            topic=topic,
            concepts=concepts,
            chunk_type=chunk_type,
            source_name=source_name,
        )
        all_chunks.append(chunk)

    if all_chunks:
        vector_store.add_chunks(all_chunks)
        # Phase 2: decompose each chunk into knowledge atoms and run conflict resolution
        for chunk in all_chunks:
            try:
                atoms = await decompose_chunk(chunk)
                for atom in atoms:
                    await process_new_atom(atom)
            except Exception:
                pass  # Knowledge decomposition is additive — never block indexing

    source = ContentSource(
        id=source_id,
        name=source_name,
        chunk_count=len(all_chunks),
        topics=sorted(all_topics),
        added_at=datetime.now().isoformat(),
    )
    save_content_source(source)
    return source


def load_content_sources() -> List[ContentSource]:
    if not CONTENT_SOURCES_PATH.exists():
        return []
    data = json.loads(CONTENT_SOURCES_PATH.read_text(encoding="utf-8"))
    return [ContentSource(**s) for s in data]


def save_content_source(source: ContentSource):
    sources = load_content_sources()
    sources = [s for s in sources if s.id != source.id]
    sources.append(source)
    CONTENT_SOURCES_PATH.write_text(
        json.dumps([s.model_dump() for s in sources], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def delete_content_source(source_id: str):
    sources = load_content_sources()
    target = next((s for s in sources if s.id == source_id), None)
    if target:
        vector_store.delete_source(target.name)
        remaining = [s for s in sources if s.id != source_id]
        CONTENT_SOURCES_PATH.write_text(
            json.dumps([s.model_dump() for s in remaining], ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
