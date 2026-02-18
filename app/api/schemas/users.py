from pydantic import BaseModel
from typing import List
from app.api.schemas.tasks import TasksResponse

class UserResponse(BaseModel):
    id: int
    tg_id: int
    username: str
    model_config = {
        "from_attributes": True
    }

class UserWithTasksResponse(BaseModel):
    id: int
    tg_id: int
    username: str
    records: List[TasksResponse]
    model_config = {
        "from_attributes": True
    }