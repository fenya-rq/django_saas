import pytest


@pytest.mark.django_db
def test_request_without_x_schema_header(client):
    """
    Request without X-SCHEMA header should return 400.
    """
    client.defaults.pop('HTTP_X_SCHEMA', None)
    resp = client.get('/contacts')
    assert resp.status_code == 400
    assert 'X-SCHEMA' in resp.json().get('detail', '')
