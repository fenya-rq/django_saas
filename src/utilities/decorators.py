from functools import wraps

from django.db.utils import ProgrammingError
from django_tenants.utils import get_public_schema_name
from ninja.errors import HttpError


def check_model_availability_for_tenant(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.tenant.schema_name == get_public_schema_name():
            raise HttpError(403, "Public Tenant can't access to shared apps model.")

        try:
            result = func(request, *args, **kwargs)
        except ProgrammingError:
            raise HttpError(404, 'Required model does not exists')
        return result

    return inner
