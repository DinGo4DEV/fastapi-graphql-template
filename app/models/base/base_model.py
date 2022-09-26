
from datetime import datetime, tzinfo
import iso8601
from pydantic import BaseModel as PydanticBaseModel, ValidationError, validator
import ujson
from humps import camelize
import pytz

from app.utils.validator import validator_transform_zone_datetime

tz = pytz.timezone("Asia/Hong_Kong")
class BaseModel(PydanticBaseModel):
    """ BaseModel inherit from Pydantic Base Model
    This Model is use for converting fields from `snake_case` to `camelCase` in models
    and using ujson for serializer and parser for better perfomance
    """
    
    class Config:
        alias_generator = lambda x: camelize(x)
        allow_population_by_field_name = True
        json_loads = ujson.loads
        json_dumps = ujson.dumps