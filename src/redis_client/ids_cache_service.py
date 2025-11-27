from src.redis_client.model import IdsCacheRedis
from src.redis_client.config import redis_client
import numpy as np
import json

redis = redis_client.get_connection()

def generate_ref(amount: str, ccy: str) -> str:
    return f"{amount}_{ccy}"

def create_ids_by_amount_cyy(amount: str, ccy: str, ids: np.ndarray, ttl: int = 3600):
    ref = generate_ref(amount, ccy)
    ids_str = json.dumps(ids.tolist(), separators=(',', ':'))
    data = IdsCacheRedis(ids=ids_str)

    redis.setex(
        name=f"ids_cache:{ref}",
        time=ttl,
        value=data.model_dump_json()
    )
    
def get_ids_by_amount_ccy(amount: str, ccy: str) -> np.ndarray | None:
    ref = generate_ref(amount, ccy)
    data = redis.get(f"ids_cache:{ref}")
    
    if not data:
        return None
    
    parsed = IdsCacheRedis.model_validate_json(data)
    ids_list = json.loads(parsed.ids)
    return np.array(ids_list, dtype=np.int16)

