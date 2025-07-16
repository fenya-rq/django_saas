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


class ContactUpdate(ContactIn):
    email: EmailStr | None = Field(None)
    name: str | None = Field(None, max_length=100)

    @field_validator('email', mode='before')
    @classmethod
    def set_empty_email(cls, v):
        return v or None

    @field_validator('name', mode='before')
    @classmethod
    def set_empty_name(cls, v):
        return v or ''
