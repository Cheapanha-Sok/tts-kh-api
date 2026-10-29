from src.redis_client.config import redis_client
import numpy as np
import logging
import redis

logger = logging.getLogger(__name__)

def generate_ref(amount: float, ccy: str) -> str:
    return f"ids_cache:{amount}_{ccy}"

def create_ids_cache(amount: float, ccy: str, ids: np.ndarray, ttl: int | None = None):
    ref = generate_ref(amount=amount, ccy=ccy)

    try:
        redis_client.get_connection().set(
            name=ref,
            value=ids.astype(np.int16).tobytes(),
            ex=ttl
        )
    except redis.exceptions.RedisError as e:
        logger.warning(f"Failed to cache ids for {ref}: {e}")

def get_ids_by_amount_ccy(amount: float, ccy: str) -> np.ndarray | None:
    ref = generate_ref(amount=amount, ccy=ccy)

    try:
        data = redis_client.get_connection().get(ref)
    except redis.exceptions.RedisError as e:
        logger.warning(f"Failed to read cached ids for {ref}: {e}")
        return None

    if not data:
        return None

    return np.frombuffer(data, dtype=np.int16)
