from django.db.utils import ProgrammingError
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination


class SafePagination(PageNumberPagination):
    def paginate_queryset(self, queryset, pagination, **kwargs):
        try:
            return super().paginate_queryset(queryset, pagination, **kwargs)
        except ProgrammingError:
            raise HttpError(404, 'Required model does not exists')
