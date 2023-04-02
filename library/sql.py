from rest_framework.decorators import permission_classes
from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.conf import settings
from .utils import now_str, epoch_str
import re
from .table import tables
from django.db import Error


@permission_classes([permissions.IsAuthenticated])
class View(views.APIView):
    @classmethod
    def post(cls, request):
        statement = request.data.get('statement', '')
        table = request.data.get('table', '')

        # insert, update
        values = request.data.get('values', {})

        # select
        columns = request.data.get('columns', [])
        conditions = request.data.get('conditions', [])
        order_by = request.data.get('order_by', '')
        is_asc = bool(request.data.get('is_asc', False))
        limit = int(request.data.get('limit', 1))
        offset = int(request.data.get('offset', 0))

        # update, delete
        pk = int(request.data.get('pk', 0))

        statements = ['insert', 'select', 'update', 'delete']
        if settings.DEBUG or request.user.is_superuser:
            statements.append('describe')

        if not isinstance(statement, str) or statement not in statements:
            return Response({'detail': 'Invalid statement'}, status.HTTP_400_BAD_REQUEST)

        if not isinstance(table, str):
            return Response({'detail': 'Invalid table'}, status.HTTP_400_BAD_REQUEST)

        if not isinstance(values, dict):
            return Response({'detail': 'Invalid values'}, status.HTTP_400_BAD_REQUEST)

        for c in values:
            if re.match(r'^\w+$', c) is None:
                return Response({'detail': 'Invalid column'}, status.HTTP_400_BAD_REQUEST)

        if not isinstance(columns, list):
            return Response({'detail': 'Invalid columns'}, status.HTTP_400_BAD_REQUEST)

        for c in columns:
            if not isinstance(c, str) or re.match(r'^\w+$', c) is None:
                return Response({'detail': 'Invalid column'}, status.HTTP_400_BAD_REQUEST)

        if not isinstance(conditions, list):
            return Response({'detail': 'Invalid conditions'}, status.HTTP_400_BAD_REQUEST)

        for c in conditions:
            if not isinstance(c, dict):
                return Response({'detail': 'Invalid condition'}, status.HTTP_400_BAD_REQUEST)

            w = c.get('where', '')
            if not isinstance(w, str) or re.match(r'^\w+$', w) is None:
                return Response({'detail': 'Invalid where clause'}, status.HTTP_400_BAD_REQUEST)

        if not isinstance(order_by, str) or (order_by != '' and re.match(r'^\w+$', order_by) is None):
            return Response({'detail': 'Invalid order_by'}, status.HTTP_400_BAD_REQUEST)

        if limit < 1:
            return Response({'detail': 'limit < 1'}, status.HTTP_400_BAD_REQUEST)

        if limit > settings.DEFAULT_PAGE_SIZE:
            return Response({'detail': 'limit > settings.DEFAULT_PAGE_SIZE'}, status.HTTP_400_BAD_REQUEST)

        if settings.NEXT_PAGE_CHECK_BY_LIMIT_PLUS_ONE:
            limit = limit + 1

        if offset < 0:
            return Response({'detail': 'offset < 0'}, status.HTTP_400_BAD_REQUEST)

        t = tables.get(table, None)
        if t is None:
            return Response({'detail': 'Invalid table'}, status.HTTP_400_BAD_REQUEST)

        if order_by == '':
            order_by = t.pk_column

        if statement == 'insert':
            values.pop(t.pk_column, None)
            values[t.deleted_time_column] = 0

            values[t.user_id_column] = request.user.id
            values[t.created_time_column] = now_str()

            if t.updated_time_column != '':
                values[t.updated_time_column] = epoch_str()

            data = t.insert(values)
            if isinstance(data, Error):
                return Response({'detail': str(data)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'last_row_id': data}, status.HTTP_200_OK)
        elif statement == 'select':
            if len(columns) == 0:
                columns.append(t.pk_column)

            data = t.select(columns, conditions, order_by, is_asc, limit, offset)
            if isinstance(data, Error):
                return Response({'detail': str(data)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(data, status.HTTP_200_OK)
        elif statement == 'update':
            values.pop(t.pk_column, None)
            values.pop(t.user_id_column, None)
            values[t.updated_time_column] = now_str()

            conditions.clear()
            conditions.append({'where': t.pk_column, 'equal': pk})
            conditions.append({'where': t.user_id_column, 'equal': request.user.id})

            data = t.update(values, conditions)
            if isinstance(data, Error):
                return Response({'detail': str(data)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'row_count': data}, status.HTTP_200_OK)
        elif statement == 'delete':
            conditions.clear()
            conditions.append({'where': t.pk_column, 'equal': pk})
            conditions.append({'where': t.user_id_column, 'equal': request.user.id})

            data = t.delete(conditions)
            if isinstance(data, Error):
                return Response({'detail': str(data)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'row_count': data}, status.HTTP_200_OK)
        elif statement == 'describe':
            data = t.describe()
            if isinstance(data, Error):
                return Response({'detail': str(data)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(data, status.HTTP_200_OK)

        return Response(None, status.HTTP_500_INTERNAL_SERVER_ERROR)
