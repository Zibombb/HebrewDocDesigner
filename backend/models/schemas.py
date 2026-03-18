from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum


class KnowledgeAtomType(str, Enum):
    CONCEPT = "concept"                    # מושג / הגדרה
    CLINICAL_INSIGHT = "clinical_insight"  # תובנה קלינית
    THINKING_PRINCIPLE = "thinking_principle"  # עקרון חשיבה
    MANAGEMENT_RULE = "management_rule"    # כלל ניהולי / פרוטוקול
    MEDICATION = "medication"              # תרופה
    PATHOGEN = "pathogen"                  # נגיף / חיידק / פרזיט
    APPROACH = "approach"                  # גישה טיפולית / אסטרטגיה
    TOPIC = "topic"                        # נושא כללי
    OTHER = "other"                        # אחר


class AtomStatus(str, Enum):
    ACTIVE = "active"
    CONFLICTED = "conflicted"
    SUPERSEDED = "superseded"


class KnowledgeAtom(BaseModel):
    id: str
    content: str                          # The granular knowledge statement
    atom_type: KnowledgeAtomType
    tags: List[str]
    source_chunks: List[str]              # ContentChunk IDs this came from
    source_names: List[str]               # Document names
    confidence: float = 1.0              # Increases when reinforced (max 2.0)
    status: AtomStatus = AtomStatus.ACTIVE
    related_to: List[str] = []           # IDs of related atoms
    conflicts_with: List[str] = []       # IDs of conflicting atoms
    superseded_by: Optional[str] = None
    created_at: str
    updated_at: str
    version: int = 1


class AtomProcessingResult(BaseModel):
    action: str  # ADD / REINFORCE / UPDATE / CONFLICT / PARALLEL
    atom_id: str
    affected_atom_id: Optional[str] = None
    message: str


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
