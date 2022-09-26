import sys,os
from importlib import import_module
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger
from pydantic import ValidationError
from starlette_exporter import PrometheusMiddleware, handle_metrics
from arango import ArangoClient
from arango.database import StandardDatabase
import aioredis

from app.models.config import config
from app.models.http_client import HTTPClient
from app.routers import *
from fastapi.responses import UJSONResponse,PlainTextResponse
from fastapi.exceptions import RequestValidationError
import logging

from app.logger import init_logging

init_logging()

def metrics_filter(record):
    if "/metrics" in record.args: return False
    return True

logging.getLogger("uvicorn.access").addFilter(metrics_filter)

app = FastAPI(title="fastapi-graphql-template",description="REST API for fastapi template",default_response_class=UJSONResponse)


app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origin_regex="https?://.*\.devhk\.dev(:\d+)?", 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(PrometheusMiddleware,app_name="fastapi-metrics", group_paths=True, prefix='fastapi_metrics',)

## Prometheus Metrics Route
app.add_route("/metrics", handle_metrics)

@app.on_event("startup")
async def startup():
    # redis =  aioredis.from_url(f"redis://{config['redis']['host']}:{config['redis']['port']}", encoding="utf8", decode_responses=True)
    pass

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc:ValidationError):
    logger.info(exc)
    return PlainTextResponse(exc.json(), status_code=422)

    
## dynamic add routers (files inside routers & `router` object)
from fastapi import APIRouter
routers = list(filter(lambda module: "router" in module,sys.modules))
for router in routers:
    module = sys.modules[router]
    for path in module.__path__:
        for obj in os.scandir(path):
            if obj.is_file() and "__init__" not in obj.name:
                module = import_module("."+obj.name[:-3],package=router)                
                app_router = getattr(module, "router",None)
                if app_router and isinstance(app_router,APIRouter) :
                    app.include_router(app_router)
    
## use the following command to start fastapi
## uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload


