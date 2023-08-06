from pydantic import BaseModel

class Answer(BaseModel):
    options: list[str] = None
    range: dict = None
