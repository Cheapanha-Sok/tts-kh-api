from sqlalchemy import Column, Integer, String, LargeBinary
from src.db.config import Base

class IdsCache(Base):
    __tablename__ = "ids_cache_kh"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    ref = Column(String(50), unique=True, nullable=False, index=True)
    ids = Column(LargeBinary, nullable=False)
