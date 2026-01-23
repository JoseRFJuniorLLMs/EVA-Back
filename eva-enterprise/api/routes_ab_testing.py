from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.ab_test_repo import ABTestRepository
from typing import List

router = APIRouter()

@router.get("/ab-tests", tags=["AB Testing"])
async def list_ab_tests(db: AsyncSession = Depends(get_db)):
    repo = ABTestRepository(db)
    return await repo.get_active_tests()

@router.post("/ab-tests", tags=["AB Testing"])
async def create_ab_test(
    test_name: str,
    description: str,
    percentage_a: int = 50,
    db: AsyncSession = Depends(get_db)
):
    repo = ABTestRepository(db)
    return await repo.create_test(test_name, description, percentage_a)

@router.get("/ab-tests/{test_name}/results", tags=["AB Testing"])
async def get_test_results(
    test_name: str,
    db: AsyncSession = Depends(get_db)
):
    repo = ABTestRepository(db)
    return await repo.get_test_results(test_name)
