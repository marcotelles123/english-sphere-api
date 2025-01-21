from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

class CheckResult(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    parent_id: str
    question: str
    answer: str
    result: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}