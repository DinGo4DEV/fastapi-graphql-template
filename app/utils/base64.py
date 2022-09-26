import base64
from app.models.base import BaseModel
from fastapi.encoders import jsonable_encoder
import ujson

from app.utils.encoder import custom_encoder
def base64_encode(v:str,encoding="utf-8"):
    return base64.urlsafe_b64encode(v.encode("utf-8")).decode("ascii")

def base64_encode_pydantic(obj:BaseModel, encoding="utf-8"):
    obj:dict = jsonable_encoder(obj,by_alias=True,custom_encoder=custom_encoder())
    return base64.urlsafe_b64encode(ujson.dumps(obj,ensure_ascii=False).encode("utf-8")).decode("ascii")