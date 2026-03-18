from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class VoiceProfile(BaseModel):
    style_description: str
    formality_level: int  # 1-10
    sentence_complexity: int  # 1-10
    vocabulary_richness: int  # 1-10
    tone_keywords: List[str]
    unique_phrases: List[str]
    rhetorical_patterns: List[str]
    writing_instruction: str
    sample_count: int = 0


class AnalyzeVoiceRequest(BaseModel):
    samples: List[str]


class ContentChunk(BaseModel):
    id: str
    text: str
    topic: str
    concepts: List[str]
    chunk_type: str  # definition / example / analysis / narrative / argument
    source_name: str


class ContentSource(BaseModel):
    id: str
    name: str
    chunk_count: int
    topics: List[str]
    added_at: str


class ProcessContentResponse(BaseModel):
    source_id: str
    source_name: str
    chunk_count: int
    topics: List[str]


class BookChapter(BaseModel):
    id: str
    title: str
    description: str
    order: int
    content: Optional[str] = None
    status: str = "pending"  # pending / generating / done


class Book(BaseModel):
    id: str
    title: str
    description: str
    chapters: List[BookChapter]
    created_at: str
    updated_at: str


class CreateBookRequest(BaseModel):
    title: str
    description: str
    chapter_ideas: Optional[str] = None
    n_chapters: int = 5


class GenerateChapterRequest(BaseModel):
    book_id: str
    chapter_id: str


class UpdateChapterContentRequest(BaseModel):
    content: str


class SearchResult(BaseModel):
    text: str
    topic: str
    source_name: str
    relevance: float
