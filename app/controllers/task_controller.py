# /controllers/task_controller.py
from fastapi import APIRouter, Depends, HTTPException, Body, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any
from bson import ObjectId
from typing import Optional

from app.services.task_service import get_tasks, has_subtasks
from app.utils.auth import get_user_session, get_user_name_from_session
from app.models.task import Task
from app.services import task_service

router = APIRouter()

def nl2br(value):
    return value.replace("\n", "<br>")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

templates.env.filters['nl2br'] = nl2br

def dict_to_task(task_dict: dict) -> Task:
    if "_id" in task_dict:
        task_dict["_id"] = ObjectId(task_dict["_id"])
    return Task.parse_obj(task_dict)

@router.post("/tasks/", response_model=Dict[str, Any])
async def create_task(request: Request, task: Task):
    created_task = await task_service.create_task(task, request)
    return created_task.dict()

@router.get("/tasks/", response_model=List[Dict[str, Any]])
async def get_tasks(request: Request):
    tasks = await task_service.get_prioritized_tasks(request)
    return [dict_to_task(task) for task in tasks]

# is this used?
@router.get("/tasks/{task_id}/", response_model=Dict[str, Any])
async def get_task(task_id: str, request: Request):
    task = await task_service.get_task(task_id, request)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.dict()

@router.put("/tasks/{task_id}/", response_model=Dict[str, Any])
async def update_task(task_id: str, task: Task, request: Request):
    updated_task = await task_service.update_task(task_id, task, request)

    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task.dict()

@router.delete("/tasks/{task_id}/")
async def delete_task(task_id: str):
    success = await task_service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")

@router.get("/task_detail/{task_id}/", response_class=HTMLResponse)
async def task_detail(request: Request, task_id: str):
    user_session = get_user_session(request)
    user_name = get_user_name_from_session(user_session)

    task = await task_service.get_task(task_id, request)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    subtasks = await task_service.get_subtasks_by_parent_task_id(task_id)
    return templates.TemplateResponse("task_detail.html", {"request": request, "task": task, "subtasks": subtasks, "user_name": user_name})


