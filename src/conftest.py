import re
from typing import Callable, Generator

import pytest
from django_tenants.utils import connection, schema_context

from contacts.models import Contact
from tenants.models import Domain, Tenant


@pytest.fixture(autouse=True)
def reset_schema_after_test() -> Generator[None, None, None]:
    """
    Automatically resets the database schema to public after each test.

    :return: None
    """
    yield
    connection.set_schema_to_public()


@pytest.fixture(autouse=True)
def create_public_tenant() -> Tenant:
    """
    Create and return the public tenant with domain 'localhost'.

    :return: Tenant instance for public schema
    """
    public_tenant = Tenant.objects.create(schema_name='public', name='Public')
    Domain.objects.create(domain='localhost', tenant=public_tenant, is_primary=True)
    return public_tenant


@pytest.fixture
def create_test_tenant() -> Tenant:
    """
    Create and return a test tenant with schema 'test' and domain 'test.localhost'.

    :return: Tenant instance for test schema
    """
    tenant = Tenant.objects.create(schema_name='test', name='Company Test')
    Domain.objects.create(domain='test.localhost', tenant=tenant, is_primary=True)
    return tenant


@pytest.fixture
def create_tenant() -> Callable[[str], Tenant]:
    """
    Return a factory function to create tenants with schema and domain based on input string.

    :return: Callable creating a Tenant instance from input string
    """

    def _create_tenant(var: str) -> Tenant:
        lowed_var = re.sub(r' ', '', var.lower())
        tenant = Tenant.objects.create(schema_name=f'{lowed_var}_schema', name=f'Company {var}')
        Domain.objects.create(domain=f'{lowed_var}.localhost', tenant=tenant, is_primary=True)
        return tenant

    return _create_tenant


@pytest.fixture
def create_test_contact(create_test_tenant) -> Contact:
    """
    Create and return a test contact within the test tenant schema.

    :return: Contact instance in test tenant
    """
    with schema_context(create_test_tenant.schema_name):
        return Contact.objects.create(name='Contact Test', email='example_test@mail.com')


@pytest.fixture
def create_contact() -> Callable[[Tenant, str], Contact]:
    """
    Return a factory function to create contacts in a given tenant schema with specified name.

    :return: Callable creating a Contact instance from tenant and name
    """

    def _create_contact(tenant: Tenant, name: str) -> Contact:
        with schema_context(tenant.schema_name):
            formatted_for_email = re.sub(r' ', '', name.lower())
            return Contact.objects.create(name=f'{name}', email=f'{formatted_for_email}@mail.com')

    return _create_contact
