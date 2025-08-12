from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.ai import (
    AITestGenerationRequest,
    AIDebugRequest,
    AIPrioritizationRequest,
    AIAnalysisResult,
)
from app.schemas.test_case import TestCaseResponse
from app.core.security import get_current_user
from app.ai_service import AIService
from app.models.db_models import TestExecution, TestCase as DBTestCase

router = APIRouter()


def get_ai_service() -> AIService:
    return AIService()


@router.post("/generate-tests", response_model=List[TestCaseResponse])
async def ai_generate_tests(
    request: AITestGenerationRequest,
    current_user: dict = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Generate test cases using AI.
    """
    try:
        test_cases = await ai_service.generate_test_cases(
            prompt=request.prompt,
            test_type=request.test_type,
            priority=request.priority,
            count=request.count,
        )
        return test_cases
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate test cases: {str(e)}",
        )


@router.post("/debug-test", response_model=AIAnalysisResult)
async def ai_debug_test(
    request: AIDebugRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Debug test failure using AI.
    """
    try:
        execution = await db.get(TestExecution, request.execution_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test execution not found",
            )

        test_case = await db.get(DBTestCase, execution.test_case_id)
        if not test_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test case not found",
            )

        result = await ai_service.debug_test_failure(
            test_case=test_case,
            error_description=request.error_description,
            logs=request.logs,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to debug test: {str(e)}",
        )


@router.post("/prioritize-tests", response_model=List[str])
async def ai_prioritize_tests(
    request: AIPrioritizationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Prioritize test cases using AI.
    """
    try:
        result = await db.execute(
            select(DBTestCase).where(DBTestCase.id.in_(request.test_case_ids))
        )
        test_cases = result.scalars().all()

        if not test_cases:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No test cases found with the provided IDs",
            )

        prioritized_ids = await ai_service.prioritize_test_cases(
            test_cases=test_cases, context=request.context
        )
        return prioritized_ids
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to prioritize tests: {str(e)}",
        )
