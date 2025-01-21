from typing import Any

from pydantic import BaseModel


class QuestionCheckRequest(BaseModel):
    id: str
    file: Any