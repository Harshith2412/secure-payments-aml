from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Any

class PaymentCreate(BaseModel):
    amount: float = Field(gt=0)
    currency: str = Field(default="usd", min_length=3, max_length=10)
    customer_ref: str = Field(default="unknown", max_length=256)
    metadata: dict[str, Any] = Field(default_factory=dict)

class PaymentCreateResponse(BaseModel):
    payment_id: int
    checkout_url: str

class HealthResponse(BaseModel):
    status: str = "ok"

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    role: str = Field(default="merchant", pattern="^(merchant|admin)$")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
