from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from database.models import AutomationTask, AutomationApproval, AutomationExecutionLog
from datetime import datetime
from typing import List, Optional

class AutomationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_pending_tasks(self, idoso_id: Optional[int] = None) -> List[AutomationTask]:
        query = select(AutomationTask).where(AutomationTask.status == 'pending')
        if idoso_id:
            query = query.where(AutomationTask.idoso_id == idoso_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_task_by_id(self, task_id: int) -> Optional[AutomationTask]:
        result = await self.db.execute(select(AutomationTask).where(AutomationTask.id == task_id))
        return result.scalar_one_or_none()

    async def approve_task(self, task_id: int, approver_id: int) -> bool:
        task = await self.get_task_by_id(task_id)
        if not task or task.status != 'pending':
            return False
        
        task.status = 'approved'
        task.approved_by = approver_id
        task.approved_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        approval = AutomationApproval(
            task_id=task_id,
            approver_id=approver_id,
            approval_status='approved',
            responded_at=datetime.utcnow()
        )
        self.db.add(approval)
        await self.db.commit()
        return True

    async def get_execution_logs(self, task_id: int) -> List[AutomationExecutionLog]:
        query = select(AutomationExecutionLog).where(AutomationExecutionLog.task_id == task_id).order_by(AutomationExecutionLog.step_number)
        result = await self.db.execute(query)
        return result.scalars().all()
