from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class AuditLogEntry(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    action: str = Field(..., example="generated_assessment")
    entity_type: str = Field(..., example="risk_assessments")
    entity_id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, example={"confidence": 0.92, "model": "XGBoost"})
    ip_address: Optional[str] = Field(None, example="192.168.1.1")
    created_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "log-789",
                "user_id": "987e6543-e21b-34d3-a456-426614174111",
                "action": "generated_assessment",
                "entity_type": "risk_assessments",
                "entity_id": "123e4567-e89b-12d3-a456-426614174000",
                "metadata": {"confidence": 0.92, "model": "XGBoost"},
                "ip_address": "192.168.1.1",
                "created_at": "2023-10-27T10:00:05Z"
            }
        }
