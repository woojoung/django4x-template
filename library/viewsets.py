from rest_framework import viewsets, status
from rest_framework.response import Response
from django.conf import settings
from library import utils
from django.core.exceptions import ObjectDoesNotExist


class MyModel:
    DoesNotExist = ObjectDoesNotExist
    objects = None


# Create your views here.
class MyModelViewSet(viewsets.ModelViewSet):
    _model = MyModel  # must be overridden
    _table = ''  # must be overridden

    _pk_column = 'id'
    _deleted_time_column = 'delete_time'

    _user_id_column = 'user_id'
    _created_time_column = 'insert_time'
    _updated_time_column = 'update_time'

    def create(self, request, *args, **kwargs):
        request.data.pop(self._pk_column, None)

        request.data[self._user_id_column] = request.user.id
        request.data[self._deleted_time_column] = 0

        request.data[self._created_time_column] = utils.now_str()
        request.data[self._updated_time_column] = utils.epoch_str()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        # ids = self.request.query_params.getlist('id', []) # models *_id > id
        ids = self.request.query_params.getlist(self._pk_column, [])
        page = int(self.request.query_params.get('page', 1))

        if len(ids) == 0:
            if page < 1:
                return Response({'detail': 'page < 1'}, status.HTTP_400_BAD_REQUEST)

            limit = settings.DEFAULT_PAGE_SIZE
            offset = (page - 1) * limit

            if settings.NEXT_PAGE_CHECK_BY_LIMIT_PLUS_ONE:
                limit = limit + 1

            stmt = 'SELECT * FROM {} WHERE {} = 0 ORDER BY {} DESC LIMIT %s OFFSET %s'.format(
                self._table, self._deleted_time_column, self._pk_column)
            rows = self._model.objects.raw(stmt, [limit, offset])
        else:
            if len(ids) > settings.DEFAULT_PAGE_SIZE:
                return Response({'detail': 'len(ids) > settings.DEFAULT_PAGE_SIZE'}, status.HTTP_400_BAD_REQUEST)

            if settings.DEFAULT_DATABASE_ENGINE == 'sqlite3':
                ints = utils.try_get_ints(ids)
                if isinstance(ints, ValueError):
                    return Response({'detail': str(ints)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

                stmt = 'SELECT * FROM {} WHERE {} IN ({}) AND {} = 0 ORDER BY {} DESC'.format(
                    self._table, self._pk_column, ', '.join(ints), self._deleted_time_column, self._pk_column)
                rows = self._model.objects.raw(stmt)
            else:  # mysql
                stmt = 'SELECT * FROM {} WHERE {} IN %s AND {} = 0 ORDER BY {} DESC'.format(
                    self._table, self._pk_column, self._deleted_time_column, self._pk_column)
                rows = self._model.objects.raw(stmt, [tuple(ids)])

        serializer = self.serializer_class(rows, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        pk = int(self.kwargs.get('pk', 0))

        try:
            obj = self._model.objects.get(pk=pk)
        except self._model.DoesNotExist:
            obj = None

        if obj is None:
            return Response(None, status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(obj)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        if self._updated_time_column == '':
            return Response(None, status.HTTP_405_METHOD_NOT_ALLOWED)

        pk = int(self.kwargs.get('pk', 0))

        request.data.pop(self._pk_column, None)
        request.data.pop(self._user_id_column, None)
        request.data[self._updated_time_column] = utils.now_str()

        try:
            obj = self._model.objects.get(pk=pk)
        except self._model.DoesNotExist:
            obj = None

        if obj is None:
            return Response(None, status.HTTP_404_NOT_FOUND)

        if getattr(obj, self._user_id_column) != request.user.id:
            return Response(None, status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        pk = int(self.kwargs.get('pk', 0))

        try:
            obj = self._model.objects.get(pk=pk)
        except self._model.DoesNotExist:
            obj = None

        if obj is None:
            return Response(None, status.HTTP_404_NOT_FOUND)

        if getattr(obj, self._user_id_column) != request.user.id:
            return Response(None, status.HTTP_403_FORBIDDEN)

        # obj.delete()
        setattr(obj, self._deleted_time_column, utils.now_int())
        obj.save()

        return Response(None, status.HTTP_200_OK)
