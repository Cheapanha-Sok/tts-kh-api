from pydantic import BaseModel

class IdsCacheRedis(BaseModel):
    ids: str