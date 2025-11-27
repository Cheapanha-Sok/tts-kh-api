import lameenc
import logging, time
from fastapi import APIRouter, Query, Request, Depends
from io import BytesIO
from fastapi.responses import Response

from src.texts.norm_number import normalize_amount
from src.exceptions.custom_exceptions import BaseAppException, ValidationException
from src.db.ids_cache_service import create_ids_cache, get_ids_by_amount_ccy
from src.db.config import get_db


synthesize_router = APIRouter()

SUPPORT_CURRENCY = {
    "KHR": ("real", "sen"),
    "USD": ("dollar", "cent")
}

def write_mp3(buffer, data, sample_rate, bitrate=32000):
    
    encoder = lameenc.Encoder()
    
    encoder.set_bit_rate(bitrate // 1000)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1)
    encoder.set_quality(7)
    
    mp3_data = encoder.encode(data.tobytes())
    mp3_data += encoder.flush()
    buffer.write(mp3_data)


def validate_request(amount: float, ccy: str):
    if amount <= 0:
        raise ValidationException(f"Amount should be greater than {amount}")
    if ccy not in SUPPORT_CURRENCY:
        raise ValidationException(f"Currency: [{ccy}] is not supported!")

async def generate_audio_data(text_norm: str, model):
    return model.run(
        text=text_norm
    )    

@synthesize_router.get("/synthesize")
async def synthesize(
    req: Request,
    amount: float = Query(...),
    ccy: str = Query(...),
    db_session = Depends(get_db)
):
    validate_request(amount, ccy)
    try:
        
        start_time = time.time()
        normalized_amount = normalize_amount(amount_str=str(amount), currency=ccy)
        normalized_text = f"បានទទួល{normalized_amount}"

        logging.info(f"Synthesize text: {normalized_text}")
        
        raw_audio_ids = await get_ids_by_amount_ccy(amount=amount, ccy=ccy, db=db_session)
        
        if raw_audio_ids is None:
            raw_audio_ids = await generate_audio_data(text_norm=normalized_text, model=req.app.state.model)
            await create_ids_cache(amount=amount, ccy=ccy, ids=raw_audio_ids, db=db_session)
        
        # raw_audio_ids = await generate_audio_data(text_norm=normalized_text, model=req.app.state.model)
        
        filename = f"audio-{amount}-{ccy}.mp3"
        
        with BytesIO() as buffer:
            
            write_mp3(
                buffer=buffer,
                data=raw_audio_ids,
                sample_rate=22050,
                bitrate=32000
            )
            
            logging.info(
                "Text-to-speech conversion completed in %.2f seconds | amount: %s | ccy: %s",
                time.time() - start_time,
                amount,
                ccy
            )
            
            buffer.seek(0)
            
            return Response(
                content=buffer.getvalue(),
                media_type="audio/mpeg",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'}
            )
            
    except Exception as e:
        logging.exception(e)
        raise BaseAppException(
            message="Something went wrong on our end. We will fix it as soon as possible",
            status_code=500
        )