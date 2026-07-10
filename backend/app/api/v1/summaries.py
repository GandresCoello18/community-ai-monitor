from fastapi import APIRouter, Depends

from app.api.deps import SummaryServiceDep, pagination_params
from app.schemas.camera import PaginatedResponse
from app.schemas.common import ApiResponse
from app.schemas.summary import SummaryGenerateRequest, SummaryResponse

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.get(
    "",
    response_model=PaginatedResponse[SummaryResponse],
    summary="List AI-generated summaries",
)
async def list_summaries(
    service: SummaryServiceDep,
    pagination: tuple[int, int] = Depends(pagination_params),
) -> PaginatedResponse[SummaryResponse]:
    page, limit = pagination
    return await service.list_summaries(page=page, limit=limit)


@router.post(
    "/generate",
    response_model=ApiResponse[SummaryResponse],
    response_model_exclude_none=True,
    status_code=201,
    summary="Generate a summary of events for a period using the LLM",
)
async def generate_summary(
    service: SummaryServiceDep,
    payload: SummaryGenerateRequest | None = None,
) -> ApiResponse[SummaryResponse]:
    request = payload or SummaryGenerateRequest()
    return await service.generate_summary(
        period_start=request.period_start,
        period_end=request.period_end,
    )
