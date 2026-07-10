from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthData(BaseModel):
    status: str = Field(examples=["ok"])


class ApiResponse[T](BaseModel):
    data: T
    meta: dict[str, object] | None = None
