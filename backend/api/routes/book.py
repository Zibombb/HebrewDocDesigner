import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
from backend.models.schemas import (
    Book, CreateBookRequest, GenerateChapterRequest, UpdateChapterContentRequest
)
from backend.services import book_generator
from backend.services.voice_analyzer import load_voice_profile

router = APIRouter(prefix="/book", tags=["book"])


@router.post("/create", response_model=Book)
async def create_book(request: CreateBookRequest):
    try:
        book = await book_generator.generate_book_outline(request)
        return book
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=List[Book])
def list_books():
    return book_generator.load_books()


@router.get("/{book_id}", response_model=Book)
def get_book(book_id: str):
    book = book_generator.load_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="הספר לא נמצא")
    return book


@router.post("/generate-chapter")
async def generate_chapter(request: GenerateChapterRequest):
    book = book_generator.load_book(request.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="הספר לא נמצא")

    chapter = next((ch for ch in book.chapters if ch.id == request.chapter_id), None)
    if not chapter:
        raise HTTPException(status_code=404, detail="הפרק לא נמצא")

    # Mark as generating
    chapter.status = "generating"
    book_generator.save_book(book)

    voice_profile = load_voice_profile()
    collected_content = []

    async def stream_with_save():
        try:
            async for text in book_generator.generate_chapter_stream(book, chapter, voice_profile):
                collected_content.append(text)
                yield f"data: {json.dumps({'text': text}, ensure_ascii=False)}\n\n"

            # Save completed chapter
            full_content = "".join(collected_content)
            book_generator.update_chapter_content(request.book_id, request.chapter_id, full_content)
            yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"
        except Exception as e:
            # Mark chapter as failed
            book_generator.update_chapter_content(request.book_id, request.chapter_id, "")
            chapter_ref = next(
                (ch for ch in book_generator.load_book(request.book_id).chapters
                 if ch.id == request.chapter_id), None
            )
            if chapter_ref:
                chapter_ref.status = "pending"
                book_generator.save_book(book_generator.load_book(request.book_id))
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        stream_with_save(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


@router.put("/{book_id}/chapters/{chapter_id}/content", response_model=Book)
def update_chapter_content(book_id: str, chapter_id: str, request: UpdateChapterContentRequest):
    book = book_generator.update_chapter_content(book_id, chapter_id, request.content)
    if not book:
        raise HTTPException(status_code=404, detail="הספר לא נמצא")
    return book


@router.delete("/{book_id}")
def delete_book(book_id: str):
    book_generator.delete_book(book_id)
    return {"message": "הספר נמחק"}
