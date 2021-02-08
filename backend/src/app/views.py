from django.shortcuts import render
from django.shortcuts import render
import json
from django.views.generic import View
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from django_filters import rest_framework as filters
from rest_framework import mixins, generics, permissions
from user.mixins import HttpResponseMixin
from user.permissions import IsStaffReadWriteOrAuthReadOnly
from user.utils import is_json
from app.models import Article

from app.serializers import ArticleSerializer
# Create your views here.

def get_id_from_request(request):
    """Small function to retrieve the Id from request
    It can either take id from get parameters
    or it can retrieve id from the input Json data
    """
    url_id = request.GET.get('id', None)
    input_json_id = None
    if is_json(request.body):
        input_json_data = json.loads(request.body)
        input_json_id = input_json_data.get("id", None)
    input_id = url_id or input_json_id or None
    return input_id

class ArticleFilter(filters.FilterSet):
    class Meta:
        model = Article
        fields = {
                    'id': ['gte', 'lte']
                    #'is_available' : ['exact']
                }
    @property
    def qs(self):
        parent_qs = super(ArticleFilter, self).qs
        return parent_qs



class ArticleAPIView(HttpResponseMixin,
                    mixins.RetrieveModelMixin,
                    generics.ListAPIView):
    """API View for the Report Model"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    #permission_classes = [permissions.IsAuthenticated]
    serializer_class = ArticleSerializer
    passed_id = None
    input_id = None
    search_fields = ('title', 'content')
    ordering_fields = ('title', 'id', 'volume_no', 'chapter_no',
                       "posted")
    filterset_class = ArticleFilter
    queryset = Article.objects.all()
    def get_queryset(self, *args, **kwargs):
        return Article.objects.all()
    def get_object(self):
        input_id = self.input_id
        queryset = self.get_queryset()
        obj = None
        if input_id is not None:
            obj = get_object_or_404(queryset, id=input_id)
            self.check_object_permissions(self.request, obj)
        return obj
    def get(self, request, *args, **kwargs):
        print(f"I am in get request {request.user}")
        self.input_id = get_id_from_request(request)
        if self.input_id is not None:
            return self.retrieve(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)


