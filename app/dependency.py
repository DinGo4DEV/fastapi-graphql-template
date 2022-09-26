from fastapi import Request
from arango import ArangoClient
from arango.database import StandardDatabase
from app.models.config import config
from app.models.http_client import HTTPClient,AsyncHTTPClient
import aioredis

from aioarango import ArangoClient as AsyncArangoClient
from aioarango.database import StandardDatabase as AsyncStandardDataBase

ARANGO_CONFIG = config['datasource']['ARANGO']
REDIS_CONFIG = config['redis']
client = ArangoClient(hosts=ARANGO_CONFIG["url"],http_client=HTTPClient())
async_client = AsyncArangoClient(hosts=ARANGO_CONFIG["url"],http_client=AsyncHTTPClient())

db = client.db(ARANGO_CONFIG['db'], username=ARANGO_CONFIG['username'],password=ARANGO_CONFIG['password'],verify=False)
db.aql.cache.configure(mode='demand', max_results=10000)


redis = aioredis.from_url(f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}/{REDIS_CONFIG['database']}")

def get_db(request: Request)->StandardDatabase:    
    return db

def get_redis(request: Request) -> aioredis.Redis:
    return redis

async def get_async_db(request:Request) -> AsyncStandardDataBase:
    return await async_client.db(ARANGO_CONFIG['db'], username=ARANGO_CONFIG['username'],password=ARANGO_CONFIG['password'],verify=False)