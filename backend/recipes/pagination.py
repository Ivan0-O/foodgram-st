from rest_framework import pagination
from rest_framework.response import Response


class PageLimitPagination(pagination.PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "limit"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        })
