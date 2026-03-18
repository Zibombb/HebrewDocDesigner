from fastapi import APIRouter, HTTPException
from backend.models.schemas import AnalyzeVoiceRequest, VoiceProfile
from backend.services import voice_analyzer

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/analyze", response_model=VoiceProfile)
async def analyze_voice(request: AnalyzeVoiceRequest):
    if not request.samples:
        raise HTTPException(status_code=400, detail="יש לספק לפחות דוגמת כתיבה אחת")
    try:
        profile = await voice_analyzer.analyze_voice_samples(request.samples)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile", response_model=VoiceProfile)
def get_profile():
    profile = voice_analyzer.load_voice_profile()
    if not profile:
        raise HTTPException(status_code=404, detail="לא נמצא פרופיל קולי")
    return profile


@router.delete("/profile")
def delete_profile():
    from backend.config import VOICE_PROFILE_PATH
    if VOICE_PROFILE_PATH.exists():
        VOICE_PROFILE_PATH.unlink()
    return {"message": "הפרופיל נמחק"}
