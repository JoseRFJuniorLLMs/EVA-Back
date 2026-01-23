from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.automation_repo import AutomationRepository
from typing import List, Optional

router = APIRouter()

@router.get("/tasks/pending", tags=["Automation"])
async def list_pending_tasks(
    idoso_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    repo = AutomationRepository(db)
    tasks = await repo.get_pending_tasks(idoso_id)
    return tasks

@router.post("/tasks/{task_id}/approve", tags=["Automation"])
async def approve_task(
    task_id: int,
    approver_id: int,
    db: AsyncSession = Depends(get_db)
):
    repo = AutomationRepository(db)
    success = await repo.approve_task(task_id, approver_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or already processed")
    return {"message": "Task approved successfully"}

@router.get("/tasks/{task_id}/logs", tags=["Automation"])
async def get_task_logs(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    repo = AutomationRepository(db)
    logs = await repo.get_execution_logs(task_id)
    return logs
