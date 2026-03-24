from pydantic import BaseModel, Field


class ReviewResponse(BaseModel):
    result: str = Field(..., min_length=1)
