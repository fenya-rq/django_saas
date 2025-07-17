from django.db.utils import ProgrammingError
from django.http import JsonResponse
from ninja import NinjaAPI

from contacts.views import router as contacts_router

api_v1 = NinjaAPI(urls_namespace='api_v1')

api_v1.add_router('v1/', contacts_router)


@api_v1.exception_handler
def custom_exception_handler(request, exc):
    if isinstance(exc, ProgrammingError):
        return JsonResponse({'detail': 'Required model does not exist'}, status=404)
    return None
