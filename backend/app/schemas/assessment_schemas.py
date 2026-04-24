from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from typing import Literal

class AssessmentInput(BaseModel):
    age_range: Literal['18-24', '25-34', '35-44', '45-54', '55+'] = Field(..., example="25-34")
    income_range: Literal['<5 LPA', '5-12 LPA', '12-25 LPA', '25+ LPA'] = Field(..., example="12-25 LPA")
    self_reported_tolerance: Literal['Low', 'Medium', 'High'] = Field(..., example="High")
    investment_horizon_years: int = Field(..., ge=1, le=40, example=15)
    primary_goal: Literal['Retirement', 'Wealth', 'ChildEdu', 'Property', 'Business', 'Marriage', 'Other'] = Field(..., example="Wealth")
    has_dependents: bool = Field(..., example=False)
    savings_level: Literal['Low', 'Medium', 'High'] = Field(..., example="High")
    debt_level: Literal['Low', 'Medium', 'High'] = Field(..., example="Low")

    class Config:
        json_schema_extra = {
            "example": {
                "age_range": "25-34",
                "income_range": "12-25 LPA",
                "self_reported_tolerance": "High",
                "investment_horizon_years": 15,
                "primary_goal": "Wealth",
                "has_dependents": False,
                "savings_level": "High",
                "debt_level": "Low"
            }
        }

class AssessmentOutput(BaseModel):
    predicted_class: str = Field(..., example="Aggressive")
    confidence_score: float = Field(..., example=0.92)
    probabilities: Dict[str, float] = Field(..., example={"Conservative": 0.05, "Moderate": 0.03, "Aggressive": 0.92})
    shap_values: Dict[str, float] = Field(..., example={"age_range": 0.15, "income_range": -0.05})
    top_5_features: List[Tuple[str, float]] = Field(..., example=[["self_reported_tolerance", 1.5], ["age_range", 0.9]])
    model_used: str = Field(..., example="XGBoost")

    class Config:
        json_schema_extra = {
            "example": {
                "predicted_class": "Aggressive",
                "confidence_score": 0.92,
                "probabilities": {"Conservative": 0.05, "Moderate": 0.03, "Aggressive": 0.92},
                "shap_values": {"age_range": 0.15, "income_range": -0.05},
                "top_5_features": [["self_reported_tolerance", 1.5], ["age_range", 0.9]],
                "model_used": "XGBoost"
            }
        }

class AssessmentHistory(BaseModel):
    id: str
    user_id: str
    input_data: AssessmentInput
    prediction: AssessmentOutput
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987e6543-e21b-34d3-a456-426614174111",
                "input_data": {
                    "age_range": "25-34",
                    "income_range": "12-25 LPA",
                    "self_reported_tolerance": "High",
                    "investment_horizon_years": 15,
                    "primary_goal": "Wealth",
                    "has_dependents": False,
                    "savings_level": "High",
                    "debt_level": "Low"
                },
                "prediction": {
                    "predicted_class": "Aggressive",
                    "confidence_score": 0.92,
                    "probabilities": {"Conservative": 0.05, "Moderate": 0.03, "Aggressive": 0.92},
                    "shap_values": {"age_range": 0.15, "income_range": -0.05},
                    "top_5_features": [["self_reported_tolerance", 1.5], ["age_range", 0.9]],
                    "model_used": "XGBoost"
                },
                "created_at": "2023-10-27T10:00:00Z"
            }
        }
