from django.conf import settings
from django.http import HttpResponseBadRequest
from django.utils.module_loading import import_string
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import connection, get_public_schema_name

from tenants.models import Tenant

DEV_PATHS = [
    '/static/devtools',
    '/api/docs',
    '/api/openapi',
]


class HeaderTenantMiddleware(TenantMainMiddleware):
    """
    Middleware to resolve tenant schema from X-SCHEMA header for multitenant routing.

    Sets database connection schema based on header value to isolate tenant data.
    Returns HTTP 400 if header missing or raises if tenant not found.
    Should be placed after SkipHeaderTenantMiddleware for proper exclusion behavior.
    """

    def _allow_path(self, request):
        return any([request.path.startswith(path) for path in DEV_PATHS])

    def process_request(self, request):
        """
        Switches schema to public, checks for skip flag, then sets tenant schema from header.
        Attaches resolved tenant to request. Returns 400 if header missing.
        """
        connection.set_schema_to_public()

        schema_name = request.headers.get('X-SCHEMA')
        if not schema_name:
            if not (settings.DEBUG and self._allow_path(request)):
                return HttpResponseBadRequest(reason='Missing X-SCHEMA header.')
            schema_name = get_public_schema_name()

        tenant = Tenant.objects.filter(schema_name=schema_name).first()
        if not tenant:
            default_tenant = self.no_tenant_found(request, schema_name)
            return default_tenant

        request.tenant = tenant
        connection.set_tenant(tenant)
        self.setup_url_routing(request)

    def no_tenant_found(self, request, schema_name):
        """
        Defines behavior when tenant not found: uses default view, shows public, or raises error.
        """
        if hasattr(settings, 'DEFAULT_NOT_FOUND_TENANT_VIEW'):
            view_path = settings.DEFAULT_NOT_FOUND_TENANT_VIEW
            view = import_string(view_path)
            if hasattr(view, 'as_view'):
                response = view.as_view()(request)
            else:
                response = view(request)
            if hasattr(response, 'render'):
                response.render()
            return response
        elif (
            hasattr(settings, 'SHOW_PUBLIC_IF_NO_TENANT_FOUND')
            and settings.SHOW_PUBLIC_IF_NO_TENANT_FOUND
        ):
            self.setup_url_routing(request=request, force_public=True)
        else:
            raise self.TENANT_NOT_FOUND_EXCEPTION('No tenant for Tenant "%s"' % schema_name)
