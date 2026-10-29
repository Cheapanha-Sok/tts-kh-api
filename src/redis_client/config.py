import redis
from src.setting import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class RedisClient:
    
    def __init__(self):
        self.host = settings.redis_host
        self.port = settings.redis_port
        self.password = settings.redis_password or None
        self._connection = None

    def get_connection(self):
        if self._connection is None:
            try:
                
                self._connection = redis.Redis(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    decode_responses=False,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True
                )
                
                self._connection.ping()
                logger.info(f"Successfully connected to Redis at {self.host}:{self.port}")

            except redis.exceptions.ConnectionError as e:
                logger.error(f"Failed to connect to redis: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected Redis error: {e}")
                raise

        return self._connection
    
    def test_connection(self):
        try:
            conn = self.get_connection()
            conn.ping()
            return True
        except Exception as e:
            logger.error(f"Redis connection test failed: {e}")
            return False


redis_client = RedisClient()