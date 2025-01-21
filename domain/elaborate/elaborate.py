from pydantic import BaseModel

class Elaborate(BaseModel):
    question: str
    answer: str
    result: str
    new_question: str
    new_question_id: str