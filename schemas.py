from pydantic import BaseModel
from pydantic import Field

class TodoBase(BaseModel):
    task: str = Field(min_length=1, max_length=100)

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    completed: bool

class TodoResponse(TodoCreate):
    id: int
    completed: bool