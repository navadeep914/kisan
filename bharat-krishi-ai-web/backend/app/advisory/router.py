from fastapi import APIRouter, HTTPException

from app.advisory import history_store
from app.advisory.advisory_service import AdvisoryService
from app.advisory.schemas import AdvisoryRequest, AdvisoryResponse, FarmerProfile

router = APIRouter()
service = AdvisoryService()


@router.on_event("startup")
async def initialize_advisory_storage() -> None:
    history_store.initialize_database()


@router.post("/query", response_model=AdvisoryResponse)
def create_advisory(request: AdvisoryRequest) -> AdvisoryResponse:
    try:
        history_store.initialize_database()
        return AdvisoryResponse(**service.respond(request.farmer_id, request.query, request.input_type))
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Advisory processing failed: {error}") from error


@router.get("/history/{farmer_id}")
def read_history(farmer_id: str, limit: int = 20):
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 100")
    history_store.initialize_database()
    return {"items": history_store.get_history(farmer_id, limit)}


@router.get("/profile/{farmer_id}")
def read_profile(farmer_id: str):
    history_store.initialize_database()
    return history_store.get_profile(farmer_id)


@router.put("/profile/{farmer_id}")
def update_profile(farmer_id: str, profile: FarmerProfile):
    history_store.initialize_database()
    return history_store.save_profile(farmer_id, profile.model_dump())


class TTSRequest(FarmerProfile.__base__):
    text: str
    language: str = "te"


@router.post("/tts")
def text_to_speech(request: TTSRequest):
    import io
    import re
    from fastapi.responses import Response
    from gtts import gTTS

    clean_text = re.sub(r"[*_#`]", "", request.text).strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    lang_map = {"te": "te", "hi": "hi", "en": "en", "te-IN": "te", "hi-IN": "hi", "en-IN": "en"}
    lang = lang_map.get(request.language)
    if not lang:
        if any("\u0c00" <= c <= "\u0c7f" for c in clean_text):
            lang = "te"
        elif any("\u0900" <= c <= "\u097f" for c in clean_text):
            lang = "hi"
        else:
            lang = "en"

    try:
        fp = io.BytesIO()
        tts = gTTS(clean_text, lang=lang)
        tts.write_to_fp(fp)
        fp.seek(0)
        return Response(content=fp.read(), media_type="audio/mpeg")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {error}") from error

