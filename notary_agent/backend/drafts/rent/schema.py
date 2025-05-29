from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date


class RentAgreementRequest(BaseModel):
    landlord_name: str
    tenant_name: str
    landlord_address: str
    tenant_address: str
    property_address: str
    rent_amount: int
    deposit_amount: int
    rent_start_date: date
    rent_end_date: date
    user_token: Optional[str] = None

    @field_validator("landlord_name", "tenant_name", "property_address")
    @classmethod
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v
