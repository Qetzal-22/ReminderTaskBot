from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db import crud
from app.api.schemas.tasks import TaskEdit
from app.api.templates import templates

task_router = APIRouter(prefix="/tasks", tags=["tasks"])

@task_router.get("/")
def get_tasks(request: Request, editing_id: int = None, db: Session = Depends(get_db)):
    records = crud.get_records(db)
    return templates.TemplateResponse("tasks_2.html", {"request": request, "records": records, "editing_id": editing_id})

@task_router.get("/table")
def get_tasks_table(request: Request, db: Session = Depends(get_db)):
    records = crud.get_records(db)
    return templates.TemplateResponse("tasks_table_2.html", {"request": request, "records": records})

@task_router.get("/editing")
def get_editing_tasks(request: Request, editing_id: int = Query(...), db: Session = Depends(get_db)):
    print("editing_id", editing_id)
    records = crud.get_records(db)
    return templates.TemplateResponse("tasks_editing.html", {"request": request, "records": records, "editing_id": editing_id})

@task_router.post("/edit")
def edit_task(data: TaskEdit = Depends(TaskEdit.as_form), db: Session = Depends(get_db)):
    crud.update_title_by_id(data.record_id, data.new_title, db)
    return RedirectResponse("/tasks", status_code=303)

@task_router.post("/delete")
def delete_task(record_id: int = Form(...), db: Session = Depends(get_db)):
    crud.delete_record(record_id, db)
    return RedirectResponse("/tasks", status_code=303)

