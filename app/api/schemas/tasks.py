from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import Form

class TasksResponse(BaseModel):
    id: int
    user_id: int
    create_at: datetime
    title: str
    time: str
    repetition: int
    day_week: str
    next_reminder: datetime
    category: str
    model_config = {
        "from_attributes": True
    }

class TaskEdit(BaseModel):
    record_id: int = Field(...)
    new_title: str = Field(..., min_length=3, max_length=50)

    @classmethod
    def as_form(cls, record_id: int = Form(...), new_title: str = Form(...)):
        return cls(record_id=record_id, new_title=new_title)