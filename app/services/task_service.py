# /services/task_service.py
import os
from app.models.task import Task
from app.models.task import TaskStatus
from app.utils.database import get_mongo_client
from app.utils.auth import get_authenticated_user
from typing import List, Optional, Tuple
from bson import ObjectId
import asyncio
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, ValidationError
from fastapi import Request

COLLECTION_NAME = os.getenv('MONGO_DB_COLLECTION_TASKS', 'tasks')
MONGO_DB_NAME = "optitasks"

def get_username(request: Request) -> str:
    authenticated_owner_email = str(request.session["user"]["email"])
    return authenticated_owner_email
   
async def create_task(task: Task, request: Request) -> Task:
    #async with await get_mongo_client() as client:
        client = await get_mongo_client()
        task.owner = get_username(request)

        result = await client[MONGO_DB_NAME][COLLECTION_NAME].insert_one(task.dict(by_alias=True))
        task.id = result.inserted_id        

        # If the task has a parent_id, set it as a string
        if task.parent_task:
            task.parent_task = str(task.parent_task)
    
        return task

async def get_tasks(request: Request):
    client = await get_mongo_client()

    owner_name = get_username(request)
    tasks = await client[MONGO_DB_NAME][COLLECTION_NAME].find({"owner": owner_name}).to_list(length=None)
    task_list = []
    for task in tasks:
        try:
            task_obj = Task(id=str(task["_id"]), **{k: v for k, v in task.items() if k not in ["_id", "id"]})
            task_list.append(task_obj)
        except ValidationError as e:
            print(f"Task with id {str(task['_id'])} was skipped due to validation error: {str(e)}")
    return task_list

async def get_task(task_id: str, request: Request) -> Task:
    #async with await get_mongo_client() as client:
    client = await get_mongo_client()

    owner_name = get_username(request)
    task = await client[MONGO_DB_NAME][COLLECTION_NAME].find_one({"_id": ObjectId(task_id), "owner": owner_name})
    if task:
        return Task(**task)
    else:
        return None

async def get_subtasks_by_parent_task_id(parent_task_id: str):
    #async with await get_mongo_client() as client:
    client = await get_mongo_client()
    subtasks = await client[MONGO_DB_NAME][COLLECTION_NAME].find({"parent_task_id": parent_task_id}).to_list(length=100)
    return subtasks

async def update_task(task_id: str, task: Task, request: Request) -> Task:
    #async with await get_mongo_client() as client:
    client = await get_mongo_client()
    task.owner = get_username(request)

    result = await client[MONGO_DB_NAME][COLLECTION_NAME].replace_one({"_id": ObjectId(task_id)}, task.dict(by_alias=True))
    if result.modified_count == 1:
        return task
    else:
        return None

async def delete_task(task_id: str) -> bool:
    #async with await get_mongo_client() as client:
    client = await get_mongo_client()
    result = await client[MONGO_DB_NAME][COLLECTION_NAME].delete_one({"_id": ObjectId(task_id)})
    return result.deleted_count == 1

async def get_prioritized_tasks(request: Request) -> List[Task]:
    # Get all the tasks
    tasks = await get_tasks(request)
   
    # Sort tasks by due_date, with the closest due date first
    sorted_tasks = sorted(tasks, key=lambda t: abs((t.due_date - datetime.now()).total_seconds()))

    return sorted_tasks

def has_subtasks(task, tasks):
    return any(subtask.parent_task == task.id for subtask in tasks)
