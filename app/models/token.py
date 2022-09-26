from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
import jwt
import ujson
import onetimepad
from app.utils.encoder import custom_encoder
from app.models.config import config

SECRET_KEY = config['SECRET_KEY']
ALGORITHM = "HS512"
ACCESS_TOKEN_EXPIRE_MINUTES = 5
oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl="/oauth/authorize",tokenUrl="/oauth/token")
class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str]
    token_type: str



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "iat":datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token:str = Depends(oauth2_scheme)):
    exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        res = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
    except jwt.exceptions.ExpiredSignatureError as e:
        exc.detail =str(e)
        raise exc
    except jwt.exceptions.InvalidSignatureError as e:
        exc.detail = str("Detected violation behaviour, you account will be banned if no stopping this behaviour")
        raise exc
        
    return res

def encrypt_code(obj:BaseModel,client_id):
    
    obj = jsonable_encoder(obj,by_alias=True,include={"plus_id","user_type","uid"},custom_encoder=custom_encoder())
    return onetimepad.encrypt(ujson.dumps(obj,ensure_ascii=False),key=client_id)

def decrypy_code(code,client_id):
    return onetimepad.decrypt(code,client_id)