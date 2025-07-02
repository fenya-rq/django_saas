from typing import List

from ninja import Router
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from ninja.pagination import paginate, PageNumberPagination

from contacts.models import Contact
from contacts.schemas import ContactIn, ContactOut

router = Router()

@router.post("/contacts", response={201: ContactOut, 400: dict})
def create_contact(request, payload: ContactIn):
    try:
        contact = Contact.objects.create(**payload.dict())
        return 201, contact
    except IntegrityError:
        return 400, {"detail": "Email already exists in this tenant."}


@router.get("/contacts", response=List[ContactOut])
@paginate(PageNumberPagination)
def list_contacts(request, email: str | None = None):
    qs = Contact.objects.all()
    if email:
        qs = qs.filter(email=email)
    return qs


@router.get("/contacts/{contact_id}", response=ContactOut)
def get_contact(request, contact_id: str):
    contact = get_object_or_404(Contact, id=contact_id)
    return contact


@router.put("/contacts/{contact_id}", response=ContactOut)
def update_contact(request, contact_id: str, payload: ContactIn):
    contact = get_object_or_404(Contact, id=contact_id)
    for attr, value in payload.dict().items():
        setattr(contact, attr, value)
    contact.save()
    return contact


@router.delete("/contacts/{contact_id}", response={204: None})
def delete_contact(request, contact_id: str):
    contact = get_object_or_404(Contact, id=contact_id)
    contact.delete()
    return 204, None