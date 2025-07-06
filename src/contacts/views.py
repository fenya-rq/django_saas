from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import PageNumberPagination, paginate

from contacts.models import Contact
from contacts.schemas import ContactIn, ContactOut, ContactUpdate
from utilities.decorators import check_model_availability_for_tenant

router = Router()


@router.get('/contacts', response=list[ContactOut])
@paginate(PageNumberPagination)
@check_model_availability_for_tenant
def list_contacts(request):
    contacts = Contact.objects.all()
    return contacts


@router.get('/contacts/{contact_id}', response=ContactOut)
@check_model_availability_for_tenant
def get_contact(request, contact_id: str):
    contact = get_object_or_404(Contact, id=contact_id)
    return contact


@router.post('/contacts', response={201: ContactOut, 400: dict})
@check_model_availability_for_tenant
def create_contact(request, payload: ContactIn):
    try:
        contact = Contact.objects.create(**payload.dict())
        return 201, contact
    except IntegrityError:
        return 400, {'detail': 'Email already exists in this tenant.'}


@router.put('/contacts/{contact_id}', response=ContactOut)
@check_model_availability_for_tenant
def update_contact(request, contact_id: str, payload: ContactUpdate):
    contact = get_object_or_404(Contact, id=contact_id)

    payload_dict = payload.dict(exclude_unset=True)

    # Set existing email if not provided new one
    if 'email' in payload_dict and payload_dict.get('email') is None:
        payload_dict['email'] = contact.email

    for attr, value in payload_dict.items():
        setattr(contact, attr, value)

    contact.save()
    return contact


@router.delete('/contacts/{contact_id}', response={204: None})
@check_model_availability_for_tenant
def delete_contact(request, contact_id: str):
    contact = get_object_or_404(Contact, id=contact_id)
    contact.delete()
    return 204, None
