from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from database.models import ABTestConfig, ABTestAssignment, ABTestMetric
from datetime import datetime
from typing import List, Optional, Dict

class ABTestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_tests(self) -> List[ABTestConfig]:
        query = select(ABTestConfig).where(ABTestConfig.enabled == True)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_test(self, test_name: str, description: str, percentage_a: int = 50) -> ABTestConfig:
        test = ABTestConfig(
            test_name=test_name,
            description=description,
            percentage_group_a=percentage_a
        )
        self.db.add(test)
        await self.db.commit()
        await self.db.refresh(test)
        return test

    async def log_metric(self, test_name: str, idoso_id: int, group: str, metric_type: str, value: float, metadata: Dict = None):
        metric = ABTestMetric(
            test_name=test_name,
            idoso_id=idoso_id,
            assigned_group=group,
            metric_type=metric_type,
            metric_value=value,
            metadata=metadata
        )
        self.db.add(metric)
        await self.db.commit()

    async def get_test_results(self, test_name: str) -> List[Dict]:
        query = select(
            ABTestMetric.assigned_group,
            ABTestMetric.metric_type,
            func.avg(ABTestMetric.metric_value).label('average'),
            func.count(ABTestMetric.id).label('samples')
        ).where(ABTestMetric.test_name == test_name).group_by(ABTestMetric.assigned_group, ABTestMetric.metric_type)
        
        result = await self.db.execute(query)
        return [dict(row._mapping) for row in result.all()]
