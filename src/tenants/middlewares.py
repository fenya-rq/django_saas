from django.http import JsonResponse, Http404
from django.utils.deprecation import MiddlewareMixin
from django_tenants.utils import connection, get_public_schema_name

from tenants.models import Tenant


class HeaderTenantMiddleware(MiddlewareMixin):
    TENANT_NOT_FOUND_EXCEPTION = Http404

    def process_request(self, request):
        # Start from public schema
        connection.set_schema_to_public()

        schema_name = request.headers.get('X-SCHEMA')
        if not schema_name:
            return JsonResponse({'detail': 'Missing X-SCHEMA header.'}, status=400)

        try:
            tenant = Tenant.objects.get(schema_name=schema_name)
        except Tenant.DoesNotExist:
            raise self.TENANT_NOT_FOUND_EXCEPTION(f'TENANT_NOT_FOUND for schema "{schema_name}".')

        tenant.domain_url = schema_name  # optional, no hostname here
        request.tenant = tenant

        # Set the connection's tenant schema (sets search_path)
        connection.set_tenant(tenant)

        # Setup URL routing if needed (same as original middleware)
        self.setup_url_routing(request)

    @staticmethod
    def setup_url_routing(request, force_public=False):
        """
        Same logic as original TenantMainMiddleware to set request.urlconf
        """
        public_schema_name = get_public_schema_name()
        if not hasattr(request, 'tenant'):
            force_public = True

        if force_public or request.tenant.schema_name == public_schema_name:
            if hasattr(request, 'urlconf'):
                del request.urlconf
            if hasattr(request, 'tenant'):
                request.urlconf = None
            return

        if hasattr(request, 'urlconf'):
            del request.urlconf
