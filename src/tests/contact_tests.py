from uuid import uuid4

import pytest
from django.db.utils import IntegrityError, ProgrammingError
from django.urls import reverse
from django_tenants.utils import connection, schema_context

from contacts.models import Contact
from tenants.models import Tenant


@pytest.mark.django_db
def test_create_contact_under_public():
    assert connection.schema_name == 'public'
    with pytest.raises(ProgrammingError):
        Contact.objects.create(name='John Doe', email='example@mail.com')


@pytest.mark.django_db
def test_create_contact_under_tenant(create_test_tenant):
    test_tenant = create_test_tenant
    with schema_context(test_tenant.schema_name):
        Contact.objects.create(name='John Doe', email='example@mail.com')


@pytest.mark.django_db
def test_update_contact_under_tenant(create_test_contact, create_test_tenant, create_contact):
    contact = create_test_contact
    with schema_context('test'):
        contact.name = 'Kim Frost'
        contact.save()

    test_contact = create_test_contact
    contact_1 = create_contact(create_test_tenant, 'Bob')
    with pytest.raises(IntegrityError):
        with schema_context('test'):
            test_contact.email = contact_1.email
            test_contact.save()


@pytest.mark.django_db
def test_list_contacts(client, create_test_tenant):
    """
    Test GET /contacts returns list of contacts.
    """
    resp = client.get(
        reverse('api_v1:list_contacts'), headers={'X-SCHEMA': create_test_tenant.schema_name}
    )
    assert resp.status_code == 200


@pytest.mark.django_db
def test_get_existing_contact(client, create_test_contact, create_test_tenant):
    url = reverse('api_v1:get_contact', kwargs={'contact_id': create_test_contact.id})
    resp = client.get(url, headers={'X-SCHEMA': create_test_tenant.schema_name})
    assert resp.status_code == 200


@pytest.mark.django_db
def test_get_nonexisting_contact(client, create_test_tenant):
    url = reverse('api_v1:get_contact', kwargs={'contact_id': uuid4()})
    resp = client.get(url, headers={'X-SCHEMA': create_test_tenant.schema_name})
    assert resp.status_code == 404


@pytest.mark.django_db
def test_create_contact_success(client, create_test_tenant):
    url = reverse('api_v1:create_contact')
    payloads = (
        {'name': 'John Doe', 'email': 'johndoe@mail.com'},
        {'name': 'Jade Doe', 'email': 'jadedoe@mail.com', 'phone': ''},
    )

    for payload in payloads:
        resp = client.post(
            url,
            data=payload,
            content_type='application/json',
            headers={'X-SCHEMA': create_test_tenant.schema_name},
        )
        assert resp.status_code == 201


@pytest.mark.django_db
def test_update_contact(client, create_contact, create_test_contact, create_test_tenant):
    url = reverse('api_v1:update_contact', kwargs={'contact_id': create_test_contact.id})
    payloads = (
        {'name': 'Eve Updated'},
        {'name': 'Eve Updated', 'email': 'updated_example@mail.com', 'phone': '66999999999'},
    )

    for payload in payloads:
        resp = client.put(
            url,
            data=payload,
            content_type='application/json',
            headers={'X-SCHEMA': create_test_tenant.schema_name},
        )
        assert resp.status_code == 200


@pytest.mark.django_db
def test_update_fields_with_none(client, create_test_contact, create_test_tenant):
    url = reverse('api_v1:update_contact', kwargs={'contact_id': create_test_contact.id})
    payload = {'email': None, 'phone': None}
    resp = client.put(
        url,
        data=payload,
        content_type='application/json',
        headers={'X-SCHEMA': create_test_tenant.schema_name},
    )
    assert resp.status_code == 200


@pytest.mark.django_db
def test_update_nonexisting_contact(client, create_test_tenant):
    url = reverse('api_v1:update_contact', kwargs={'contact_id': uuid4()})
    payload = {'name': 'Ghost'}
    resp = client.put(
        url,
        data=payload,
        content_type='application/json',
        headers={'X-SCHEMA': create_test_tenant.schema_name},
    )
    assert resp.status_code == 404


@pytest.mark.django_db
def test_delete_existing_contact(client, create_test_contact, create_test_tenant):
    url = reverse('api_v1:delete_contact', kwargs={'contact_id': create_test_contact.id})
    resp = client.delete(url, headers={'X-SCHEMA': create_test_tenant.schema_name})
    assert resp.status_code == 204


@pytest.mark.django_db
def test_request_without_x_schema_header(client) -> None:
    """
    Test GET /admin without X-SCHEMA header.

    Ensures:
    - Returns HTTP 400 status code.
    - Response includes 'X-SCHEMA' mention in detail message.
    """
    resp = client.get('/admin')
    assert resp.status_code == 400
    assert resp.reason_phrase == 'Missing X-SCHEMA header.'


@pytest.mark.django_db
def test_request_with_invalid_x_schema_header(client) -> None:
    """
    Test GET with invalid X-SCHEMA header.

    Ensures:
    - Returns HTTP 404 error when schema does not exist.
    """
    resp = client.get('/admin', headers={'X-SCHEMA': 'nonexistent'})
    assert resp.status_code == 404


@pytest.mark.django_db
def test_request_wit_x_schema_header(client) -> None:
    """
    Test GET /admin wit X-SCHEMA header.

    Ensures:
    - Returns HTTP 301 status code.
    - Response that redirect to admin log in page.
    """
    public_tenant = Tenant.objects.first()
    resp = client.get('/admin', headers={'X-SCHEMA': public_tenant.schema_name})
    assert resp.status_code == 301


@pytest.mark.django_db
def test_cross_tenant_requests(
    client, create_contact, create_tenant, create_test_contact, create_test_tenant
) -> None:
    """
    Test cross-tenant contact access isolation.

    Ensures:
    - Contact from tenant A is not accessible using tenant B's schema.
    - Returns 404 for cross-tenant GET requests.
    """

    bigco = create_tenant('BigCo')
    bigco_contact = create_contact(bigco, 'John Doe')

    url = reverse('api_v1:get_contact', kwargs={'contact_id': create_test_contact.id})
    failed_cross_response = client.get(url, headers={'X-SCHEMA': bigco.schema_name})

    url = reverse('api_v1:delete_contact', kwargs={'contact_id': bigco_contact.id})
    failed_cross_response_reversed = client.get(
        url, headers={'X-SCHEMA': create_test_tenant.schema_name}
    )

    assert failed_cross_response.status_code == 404
    assert failed_cross_response_reversed.status_code == 404


@pytest.mark.django_db
def test_unique_email_per_schema(create_contact, create_tenant, create_test_tenant) -> None:
    """
    Test email uniqueness constraint within tenant schema.

    Ensures:
    - Same email can exist in different tenants.
    - Creating duplicate email within one tenant raises IntegrityError.
    """
    bigco = create_tenant('BigCo')
    bigco_contact = create_contact(bigco, 'John Doe')

    # Attempt to create contact with existing email from company1 for company2
    with schema_context(create_test_tenant.schema_name):
        Contact.objects.create(name=bigco_contact.name, email=bigco_contact.email)

    # # Attempt to create contact with existing email for company1
    with pytest.raises(IntegrityError):
        with schema_context(bigco.schema_name):
            Contact.objects.create(name=bigco_contact.name, email=bigco_contact.email)
