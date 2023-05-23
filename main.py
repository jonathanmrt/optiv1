# main.py
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from typing import List
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

from app.utils.database import get_mongo_client_sync
from app.services.task_service import get_tasks, has_subtasks
from app.utils.auth import get_user_session, get_user_name_from_session
from app.controllers import task_controller, user_controller
from app.models.task import Task
from app.models.user import UserInDB

app = FastAPI()

# Authentication
app.add_middleware(
    SessionMiddleware, secret_key="SECRET_KEY"
)

# Mount the static folder
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Include task and user routes
app.include_router(task_controller.router)
app.include_router(user_controller.router)

@app.get("/favicon.ico", response_class=FileResponse)
async def get_favicon():
    return FileResponse("app/static/favicon.ico")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        user_session = get_user_session(request)
        user_name = get_user_name_from_session(user_session)

        return templates.TemplateResponse("index.html", {"request": request, "user_name": user_name})
    except:
        return templates.TemplateResponse("login.html", {"request": request})

@app.get("/tasks", response_class=HTMLResponse)
async def tasks(request: Request):
    user_session = get_user_session(request)
    user_name = get_user_name_from_session(user_session)

    tasks = await task_controller.get_tasks(request)
    task_has_subtasks = {task.id: has_subtasks(task, tasks) for task in tasks}
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks, "task_has_subtasks": task_has_subtasks, "user_name": user_name})

@app.get("/task_detail/{task_id}", response_class=HTMLResponse)
async def task_detail(request: Request, task_id: str):
    user_session = get_user_session(request)
    user_name = get_user_name_from_session(user_session)

    task = await task_controller.get_task(task_id, request)
    return templates.TemplateResponse("task_detail.html", {"request": request, "task": task, "user_name": user_name})

@app.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/logout")
def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
