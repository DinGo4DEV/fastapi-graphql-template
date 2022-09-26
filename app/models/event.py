from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum

from pydantic import Extra, Field
from app.models.base import BaseModel

class ActionEnum(str,Enum):
    create= "created"
    update= "updated"
    delete = "deleted"
    toggle = "toggled"
    toggle_bookmark = "toggled_bookmark"
    

class Event(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    eta: datetime = Field(default_factory=datetime.utcnow)
    
    
class AuditEvent(Event):
    action: str
    author: str 
           

class CreateEvent(AuditEvent):
    action = ActionEnum.create.value
    new : dict
    old:dict = None
    
class UpdateEvent(AuditEvent):
    action = ActionEnum.update.value
    new : dict
    old : Optional[dict]
    
class DeleteEvent(AuditEvent):
    action = ActionEnum.delete.value
    new : Optional[dict]
    old : Optional[dict]

class ToggleEvent(AuditEvent):
    action: str
    new: Optional[dict]
    old: Optional[dict]

