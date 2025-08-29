from pydantic import BaseModel
from typing import TypedDict, List

class Quotes(BaseModel):
    quotes: List[str]

class State(TypedDict):
    article: str
    summary: str
    quotes: Quotes
    insta_caption: str