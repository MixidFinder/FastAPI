import json
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str]


tasks = []


def load_tasks():
    global tasks
    with open("tasks.json", "r") as f:
        tasks = json.load(f)


def save_tasks():
    global tasks
    with open("tasks.json", "w") as f:
        json.dump(tasks, f, indent=4)


@app.get("/tasks/")
async def get_tasks():
    load_tasks()
    logger.info("Tasks loaded")
    return {"tasks": tasks}


@app.post("/tasks/")
async def create_task(task: Task = Body(...)):
    load_tasks()
    task.id = len(tasks) + 1
    tasks.append(task)
    save_tasks()
    logger.info("Task created")
    return {"task": task}


@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    load_tasks()
    task = next((t for t in tasks if t.id == task_id), None)
    logger.info(f"Task found by id: {task_id}")
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return {"task": task}


@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: Task = Body(...)):
    load_tasks()
    task_to_update = next((t for t in tasks if t.id == task_id), None)
    if task_to_update is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    task_to_update.title = task.title
    task_to_update.description = task.description
    logger.info(f"Task updated by id: {task_id}")
    save_tasks()
    return {"task": task_to_update}


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    load_tasks()
    task_to_delete = next((t for t in tasks if t.id == task_id), None)
    if task_to_delete is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    tasks.remove(task_to_delete)
    logger.info(f"Task removed by id: {task_id}")
    save_tasks()
    return {"message": "Задача успешно удалена"}
