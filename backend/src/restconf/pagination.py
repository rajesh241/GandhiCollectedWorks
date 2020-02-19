"""Default Pagination class application to all APIs"""
from rest_framework import pagination
from rest_framework.response import Response
import math

class LibtechAPIPagination(pagination.LimitOffsetPagination): #PageNumberPagination):
    """Default Pagination class"""
    #page_size   =  20
    default_limit = 20
    max_limit = 10000
    #limit_query_param = 'lim'

class CustomPagination(pagination.LimitOffsetPagination):
    default_limit = 20
    max_limit = 10000

    def get_paginated_response(self, data):
        return Response({
               'next': self.get_next_link(),
               'previous': self.get_previous_link(),
            'count': self.count,
            'page_no' : int(self.offset/self.limit)+1,
            'total_pages' : math.ceil(self.count/self.limit),
           # 'total_pages': self.page.paginator.num_pages,
            'results': data
        })
