from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RecommendationRequest(BaseModel):
    assessment_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")

    class Config:
        json_schema_extra = {
            "example": {
                "assessment_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }

class FundRecommendation(BaseModel):
    id: Optional[str] = None
    assessment_id: str
    user_id: str
    fund_name: str = Field(..., example="Vanguard Total Stock Market Index Fund")
    fund_type: str = Field(..., example="Equity")
    narrative: str = Field(..., example="Based on your Aggressive risk profile, this fund provides optimal diversification for high growth.")
    rationale_points: List[str] = Field(..., example=["Low expense ratio", "Broad market exposure", "Aligned with long-term horizon"])
    suitability_score: float = Field(..., example=0.94)
    created_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174999",
                "assessment_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987e6543-e21b-34d3-a456-426614174111",
                "fund_name": "Vanguard Total Stock Market Index Fund",
                "fund_type": "Equity",
                "narrative": "Based on your Aggressive risk profile, this fund provides optimal diversification for high growth.",
                "rationale_points": ["Low expense ratio", "Broad market exposure", "Aligned with long-term horizon"],
                "suitability_score": 0.94,
                "created_at": "2023-10-27T10:05:00Z"
            }
        }
