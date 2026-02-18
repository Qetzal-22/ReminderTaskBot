from app.db.database import get_db
from app.db import crud
from app.api.schemas.users import UserResponse, UserWithTasksResponse
from app.api.templates import templates

from typing import List
from fastapi import Depends, APIRouter, Request
from sqlalchemy.orm import Session

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.get("/")
def get_users(request: Request, db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return templates.TemplateResponse("/users_2.html", {"request": request, "users": users})

@user_router.get("/{user_id}", response_model=UserWithTasksResponse)
def get_user(user_id:int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(user_id, db)
    for record in user.records:
        record.time = record.time.strftime("%H:%M")
    return user