from pydantic import BaseModel, field_validator, Field
from typing import Optional
from datetime import date


class PartnershipDeedRequest(BaseModel):
    firm_name: str
    business_type: str

    partner1_full_name: str = Field(alias="partner1_full_name")
    partner1_father_name: str = Field(alias="partner1_father_name")
    partner1_age: str = Field(alias="partner1_age")
    partner1_address: str = Field(alias="partner1_address")

    partner2_full_name: str = Field(alias="partner2_full_name")
    partner2_father_name: str = Field(alias="partner2_father_name")
    partner2_age: str = Field(alias="partner2_age")
    partner2_address: str = Field(alias="partner2_address")

    capital_contribution: str
    profit_sharing: str
    duties: str

    execution_date: Optional[date] = None
    jurisdiction: Optional[str] = None
    business_address: Optional[str] = None
    area_of_operation: Optional[str] = None
    start_date: Optional[date] = None
    user_token: Optional[str] = None

    @field_validator("capital_contribution", "profit_sharing")
    @classmethod
    def validate_comma_separated_pair(cls, v, info):
        parts = v.split(",")
        if len(parts) != 2:
            raise ValueError(
                f"{info.field_name} must contain two comma-separated values (e.g., '50,50')"
            )
        return v

    @field_validator("firm_name", "business_type", "duties", mode="before")
    @classmethod
    def not_empty(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("Field cannot be empty")
        return v
