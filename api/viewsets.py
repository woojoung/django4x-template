from django.shortcuts import render
from rest_framework import permissions
from library.viewsets import MyModelViewSet
from .serializers import UserSerializer, FamilySerializer


# Create your views here.

class UserViewSet(MyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'get', 'put', 'delete']

    _model = serializer_class.Meta.model
    _table = _model.Meta.db_table
    _pk_column = 'user_id'
