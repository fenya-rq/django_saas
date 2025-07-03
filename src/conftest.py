import pytest
from django_tenants.utils import schema_context

from contacts.models import Contact
from tenants.models import Domain, Tenant


@pytest.fixture
def setup_tenant_with_contacts() -> tuple[Tenant, Tenant, Tenant]:
    public_tenant = Tenant.objects.create(schema_name='public', name='Public')
    Domain.objects.create(domain='localhost', tenant=public_tenant, is_primary=True)

    bigco = Tenant.objects.create(schema_name='bigco', name='Big company')
    Domain.objects.create(domain='sub1.localhost', tenant=bigco, is_primary=True)

    smallco = Tenant.objects.create(schema_name='smallco', name='Small company')
    Domain.objects.create(domain='sub2.localhost', tenant=smallco, is_primary=True)

    return public_tenant, bigco, smallco


@pytest.fixture
def create_contacts(setup_tenant_with_contacts) -> tuple[Contact, Contact]:
    _, bigco, smallco = setup_tenant_with_contacts

    with schema_context(bigco.schema_name):
        bigco_contact = Contact.objects.create(name='John Doe', email='ex@mail.com')

    with schema_context(smallco.schema_name):
        smallco_contact = Contact.objects.create(name='Peter Pan', email='ex@mail.com')

    return bigco_contact, smallco_contact
