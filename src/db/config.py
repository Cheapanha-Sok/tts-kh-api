from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.setting import get_settings
from urllib.parse import quote_plus
import logging

settings = get_settings()

class DataBaseConfig:
    
    def __init__(self):
        self.host = settings.postgres_host
        self.user = settings.postgres_user
        self.db = settings.postgres_db
        self.port = settings.postgres_port
        self.password = settings.postgres_password
        
    @staticmethod
    def encode_password(password: str) -> str:
        return quote_plus(password)

    def get_database_url(self, is_encode: bool=False):
        password = self.encode_password(self.password) if is_encode else self.password
        return f"postgresql://{self.user}:{password}@{self.host}:{self.port}/{self.db}"

db_config = DataBaseConfig()

db_url = db_config.get_database_url(is_encode=True)
logging.info(f"Database url: {db_url}")

engine = create_engine(url=db_url, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def create_db_tables():
    Base.metadata.create_all(engine)