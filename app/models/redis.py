from redis import Redis
from pottery import Redlock
from app.models.config import config

REDIS_CONFIG = config['redis']
redis = Redis.from_url(f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}/1")
