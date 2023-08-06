from pydantic import BaseModel
from Models.Answer import Answer
from Enums.QuestionType import QuestionType

class Question(BaseModel):
    type: QuestionType
    text: str
    order: int
    answer: Answer = None
