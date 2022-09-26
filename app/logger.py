"""Configure handlers and formats for application loggers."""
import functools
import logging
import sys
from pprint import pformat

# if you dont like imports of private modules
# you can move it to typing.py module
from loguru import logger
from loguru._defaults import env as loguru_env
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from app.utils.encoder import custom_encoder

LOGGING_FORMAT = loguru_env(
    "LOGGING_FORMAT",
    str,
    "<green>{time:YYYY-MM-DDTHH:mm:ss.SSSZ}</green> | "
    "<level>{level: <5}</level> | "
    "<level>{message}</level>",
)

class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict) -> str:
    """
    Custom format for loguru loggers.
    Uses pformat for log any data like request/response body during debug.
    Works with logging if loguru handler it.

    Example:
    >>> payload = [{"users":[{"name": "Nick", "age": 87, "is_active": True}, {"name": "Alex", "age": 27, "is_active": True}], "count": 2}]
    >>> logger.bind(payload=).debug("users payload")
    >>> [   {   'count': 2,
    >>>         'users': [   {'age': 87, 'is_active': True, 'name': 'Nick'},
    >>>                      {'age': 27, 'is_active': True, 'name': 'Alex'}]}]
    """
    format_string = LOGGING_FORMAT
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string


def init_logging():
    """
    Replaces logging handlers with a handler for using the custom handler.
        
    WARNING!
    if you call the init_logging in startup event function, 
    then the first logs before the application start will be in the old format

    >>> app.add_event_handler("startup", init_logging)
    stdout:
    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [11528] using statreload
    INFO:     Started server process [6036]
    INFO:     Waiting for application startup.
    2020-07-25 02:19:21.357 | INFO     | uvicorn.lifespan.on:startup:34 - Application startup complete.
    
    """

    # disable handlers for specific uvicorn loggers
    # to redirect their output to the default uvicorn logger
    # works with uvicorn==0.11.6
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("uvicorn.")
    )
    
    intercept_handler = InterceptHandler()
    # change handler for default uvicorn logger
    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = [intercept_handler]

    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    # set logs output, level and format
    logger.configure(
        handlers=[{"sink": sys.stdout, "level": logging.INFO, "format": format_record,"serialize": False}]
    )

def _logging_entry(logger_,name,entry=True,level=logging.DEBUG, *args,**kwargs):
    if entry:
        log_dict = {}
        for key,value in kwargs.items():
            if isinstance(value,BaseModel): 
                log_dict[key] = jsonable_encoder(value,exclude_unset=True,custom_encoder=custom_encoder())
        logger_.log(level, "/{} {}", name, log_dict)
        
def _logging_exit(logger_,name,result,exit=True,level=logging.DEBUG, *args,**kwargs):
    if exit:
        logger_.log(level, "Exiting '{}' (result={})", name,result )

def logger_wraps(*, entry=True, exit=True, level="INFO"):
    
    def wrapper(func):
        name = func.__name__
        
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            _logging_entry(logger_,name,entry,level,*args,**kwargs)
            result = func(*args, **kwargs)
            _logging_exit(logger_,name,result,exit,level,*args,**kwargs)
            return result
        
        return wrapped

    return wrapper

def logger_wraps_async(*, entry=True, exit=True, level="INFO"):
    
    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            _logging_entry(logger_,name,entry,level,*args,**kwargs)
            result = await func(*args, **kwargs)
            _logging_exit(logger_,name,result,exit,level,*args,**kwargs)
            return result

        return wrapped

    return wrapper