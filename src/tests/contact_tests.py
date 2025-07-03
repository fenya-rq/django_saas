import pytest
from django.db.utils import IntegrityError
from django_tenants.utils import connection, schema_context

from contacts.models import Contact


@pytest.mark.django_db
def test_request_without_x_schema_header(client) -> None:
    """
    Test GET /contacts without X-SCHEMA header.

    Ensures:
    - Returns HTTP 400 status code.
    - Response includes 'X-SCHEMA' mention in detail message.
    """
    resp = client.get('/contacts')
    assert resp.status_code == 400
    assert 'X-SCHEMA' in resp.json().get('detail', '')


@pytest.mark.django_db
def test_cross_tenant_requests(create_tenant, create_contact, client) -> None:
    """
    Test cross-tenant contact access isolation.

    Ensures:
    - Contact from tenant A is not accessible using tenant B's schema.
    - Returns 404 for cross-tenant GET requests.
    """

    company1, company2 = create_tenant(1), create_tenant(2)
    company1_contact1, company2_contact2 = create_contact(company1), create_contact(company2)

    failed_cross_response = client.get(
        f'/api/v1/contacts/{company1_contact1.id}', headers={'X-SCHEMA': company2.schema_name}
    )

    failed_cross_response_reversed = client.get(
        f'/api/v1/contacts/{company2_contact2.id}', headers={'X-SCHEMA': company1.schema_name}
    )

    assert failed_cross_response.status_code == 404
    assert failed_cross_response_reversed.status_code == 404
    connection.set_schema_to_public()


@pytest.mark.django_db
def test_unique_email_per_schema(create_tenant, create_contact) -> None:
    """
    Test email uniqueness constraint within tenant schema.

    Ensures:
    - Same email can exist in different tenants.
    - Creating duplicate email within one tenant raises IntegrityError.
    """
    company1, company2 = create_tenant(1), create_tenant(2)

    company1_contact1 = create_contact(company1)

    # Attempt to create contact with existing email from company1 for company2
    with schema_context(company2.schema_name):
        Contact.objects.create(name=company1_contact1.name, email=company1_contact1.email)

    # Attempt to create contact with existing email for company1
    with pytest.raises(IntegrityError):
        with schema_context(company1.schema_name):
            Contact.objects.create(name=company1_contact1.name, email=company1_contact1.email)
