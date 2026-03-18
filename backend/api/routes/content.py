from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from backend.models.schemas import ContentSource
from backend.services import content_processor
from backend.services.vector_store import get_collection_count, get_all_topics

router = APIRouter(prefix="/content", tags=["content"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}


@router.post("/upload", response_model=ContentSource)
async def upload_content(file: UploadFile = File(...)):
    from pathlib import Path
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"סוג קובץ לא נתמך. קבצים נתמכים: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    try:
        content = await file.read()
        source = await content_processor.process_file(file.filename, content)
        return source
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources", response_model=List[ContentSource])
def list_sources():
    return content_processor.load_content_sources()


@router.delete("/sources/{source_id}")
def delete_source(source_id: str):
    content_processor.delete_content_source(source_id)
    return {"message": "המקור נמחק"}


@router.get("/topics")
def list_topics():
    return {"topics": get_all_topics(), "total_chunks": get_collection_count()}
