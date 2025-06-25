from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class LoanAgreementRequest(BaseModel):
    lender_name: str = Field(..., alias="lender_name")
    borrower_name: str = Field(..., alias="borrower_name")
    loan_amount: float = Field(..., alias="loan_amount")
    loan_period_months: int = Field(..., alias="loan_period_months")
    loan_start_date: date = Field(..., alias="loan_start_date")
    interest_rate_percent: float = Field(..., alias="interest_rate_percent")
    repayment_option: str = Field(..., alias="repayment_option")  # "One-time" or "EMI"
    monthly_installment_amount: Optional[float] = Field(
        None, alias="monthly_installment_amount"
    )
    user_token: Optional[str] = Field(None, alias="user_token")
