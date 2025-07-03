import pytest


@pytest.mark.django_db
def test_request_without_x_schema_header(client):
    """
    Request without X-SCHEMA header should return 400.
    """
    resp = client.get('/contacts')
    assert resp.status_code == 400
    assert 'X-SCHEMA' in resp.json().get('detail', '')


@pytest.mark.django_db
def test_tenants_isolation(setup_tenant_with_contacts, create_contacts, client) -> None:
    _, bigco, smallco = setup_tenant_with_contacts
    bigco_contact, smallco_contact = create_contacts

    failed_cross_response = client.get(
        f'/api/v1/contacts/{bigco_contact.id}', headers={'X-SCHEMA': smallco.schema_name}
    )

    failed_cross_response_reversed = client.get(
        f'/api/v1/contacts/{smallco_contact.id}', headers={'X-SCHEMA': bigco.schema_name}
    )

    assert failed_cross_response.status_code == 404
    assert failed_cross_response_reversed.status_code == 404
