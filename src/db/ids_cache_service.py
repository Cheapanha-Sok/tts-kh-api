from src.models.ids_cache import IdsCache
from sqlalchemy.orm import Session
import numpy as np

def generate_ref(amount: float, ccy: str) -> str:
    return f"{amount}_{ccy}"

async def create_ids_cache(amount: float, ccy: str, ids: np.ndarray, db: Session):
    ref = generate_ref(amount=amount, ccy=ccy)

    ids_bytes = ids.tobytes()

    db.add(
        IdsCache(
            ref=ref,
            ids=ids_bytes
        )
    )
    db.commit()

    
async def get_ids_by_amount_ccy(amount: float, ccy: str, db: Session):
    ref = generate_ref(amount=amount, ccy=ccy)
    
    row = db.query(IdsCache).filter(IdsCache.ref == ref).first()

    if not row:
        return None

    return np.frombuffer(row.ids, dtype=np.int16)