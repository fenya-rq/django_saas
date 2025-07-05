from datetime import date
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactIn(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    phone: str | None = Field('', max_length=11)

    @field_validator('phone', mode='before')
    @classmethod
    def set_empty_phone(cls, v):
        return v or ''

    class Config:
        from_attributes = True


class ContactOut(ContactIn):
    id: UUID
    date_created: date

    class Config:
        from_attributes = True
