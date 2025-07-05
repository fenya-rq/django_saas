from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import PageNumberPagination, paginate

from contacts.models import Contact
from contacts.schemas import ContactIn, ContactOut
from utilities.decorators import check_model_availability_for_tenant

router = Router()


@router.post('/contacts', response={201: ContactOut, 400: dict})
def create_contact(request, payload: ContactIn):
    try:
        contact = Contact.objects.create(**payload.dict())
        return 201, contact
    except IntegrityError:
        return 400, {'detail': 'Email already exists in this tenant.'}


@router.get('/contacts', response=list[ContactOut])
@paginate(PageNumberPagination)
@check_model_availability_for_tenant
def list_contacts(request):
    contacts = Contact.objects.all()
    return contacts


@router.get('/contacts/{contact_id}', response=ContactOut)
def get_contact(request, contact_id: str):
    contact = get_object_or_404(Contact, id=contact_id)
    return contact


@router.put('/contacts/{contact_id}', response=ContactOut)
def update_contact(request, contact_id: str, payload: ContactIn):
    contact = get_object_or_404(Contact, id=contact_id)
    for attr, value in payload.dict().items():
        setattr(contact, attr, value)
    contact.save()
    return contact


@router.delete('/contacts/{contact_id}', response={204: None})
def delete_contact(request, contact_id: str):
    contact = get_object_or_404(Contact, id=contact_id)
    contact.delete()
    return 204, None
