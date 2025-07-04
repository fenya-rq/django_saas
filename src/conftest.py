import itertools
from typing import Callable

import pytest
from django_tenants.utils import schema_context

from contacts.models import Contact
from tenants.models import Domain, Tenant


@pytest.fixture(autouse=True)
def setup_public_tenant() -> Tenant:
    """Automatically sets up the public tenant for tests."""
    public_tenant = Tenant.objects.create(schema_name='public', name='Public')
    Domain.objects.create(domain='localhost', tenant=public_tenant, is_primary=True)
    return public_tenant


@pytest.fixture
def create_tenant() -> Callable[[int], Tenant]:
    """Return a factory to create tenants with a given ID."""

    def _create_tenant(id_) -> Tenant:
        tenant = Tenant.objects.create(schema_name=f'company_{id_}', name=f'Company {id_}')
        Domain.objects.create(domain=f'sub{id_}.localhost', tenant=tenant, is_primary=True)
        return tenant

    return _create_tenant


@pytest.fixture
def create_contact() -> Callable[[Tenant], Contact]:
    """Return a factory to create contacts within a specified tenant schema."""
    counter = itertools.count(1)

    def _create_contact(tenant) -> Contact:
        with schema_context(tenant.schema_name):
            id_ = next(counter)
            return Contact.objects.create(name=f'Contact {id_}', email=f'example{id_}@mail.com')

    return _create_contact
