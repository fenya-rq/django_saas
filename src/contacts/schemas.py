from datetime import date
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ContactIn(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    phone: str | None = Field(None, max_length=11)

    class Config:
        from_attributes = True


class ContactOut(ContactIn):
    id: UUID
    date_created: date

    class Config:
        from_attributes = True
