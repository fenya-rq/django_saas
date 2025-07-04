from django.conf import settings
from django.http import HttpResponseBadRequest
from django.utils.module_loading import import_string
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import connection

from tenants.models import Tenant


class HeaderTenantMiddleware(TenantMainMiddleware):
    def process_request(self, request):
        connection.set_schema_to_public()

        schema_name = request.headers.get('X-SCHEMA')
        if not schema_name:
            return HttpResponseBadRequest(reason='Missing X-SCHEMA header.')

        tenant = Tenant.objects.filter(schema_name=schema_name).first()
        if not tenant:
            default_tenant = self.no_tenant_found(request, schema_name)
            return default_tenant

        request.tenant = tenant
        connection.set_tenant(tenant)
        self.setup_url_routing(request)

    def no_tenant_found(self, request, schema_name):
        """What should happen if no tenant is found.
        This makes it easier if you want to override the default behavior"""
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
