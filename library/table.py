from django.db import connections, Error
from django.conf import settings
from library.utils import row_to_dict, now_int


class Table:
    def __init__(self, database, table, pk_column, deleted_time_column, user_id_column, created_time_column,
                 updated_time_column):
        self.database = database
        self.table = table

        self.pk_column = pk_column
        self.deleted_time_column = deleted_time_column

        self.user_id_column = user_id_column
        self.created_time_column = created_time_column
        self.updated_time_column = updated_time_column

        self._params = []
        self._stmt_parts = []

    def clear(self):
        self._params.clear()
        self._stmt_parts.clear()

    def where(self, conditions):
        _where = ''

        _equal = None
        _like = ''
        _in = []

        _in_place_holders = []
        for c in conditions:
            _where = c.get('where', '')

            _equal = c.get('equal', None)
            _like = c.get('like', '')
            _in = c.get('in', [])

            if not isinstance(_in, list):
                return Error('not isinstance(_in, list)')

            if len(_in) > settings.DEFAULT_PAGE_SIZE:
                return Error('len(_in) > settings.DEFAULT_PAGE_SIZE')

            if _equal is not None:
                self._stmt_parts.append('AND')
                self._stmt_parts.append(_where)
                self._stmt_parts.append('= %s')

                self._params.append(_equal)
            elif _like != '':
                self._stmt_parts.append('AND')
                self._stmt_parts.append(_where)
                self._stmt_parts.append('LIKE %s')

                self._params.append('%' + _like + '%')
            elif len(_in) > 0:
                _in_place_holders.clear()
                for p in _in:
                    _in_place_holders.append('%s')
                    self._params.append(p)

                self._stmt_parts.append('AND')
                self._stmt_parts.append(_where)
                self._stmt_parts.append('IN (')
                self._stmt_parts.append(', '.join(_in_place_holders))
                self._stmt_parts.append(')')
            else:
                return Error('Invalid where clause')

    def insert(self, values):
        self.clear()

        columns = []
        place_holders = []
        for k, v in values.items():
            columns.append(k)
            place_holders.append('%s')
            self._params.append(v)

        self._stmt_parts.append('INSERT INTO')
        self._stmt_parts.append(self.table)
        self._stmt_parts.append('(' + ', '.join(columns) + ')')
        self._stmt_parts.append('VALUES(' + ', '.join(place_holders) + ')')

        stmt = ' '.join(self._stmt_parts)
        cursor = connections[self.database].cursor()

        try:
            cursor.execute(stmt, self._params)
            result = cursor.lastrowid
        except Error as error:
            result = error
        finally:
            cursor.close()

        return result

    def select(self, columns, conditions, order_by, is_asc, limit, offset):
        self.clear()

        self._stmt_parts.append('SELECT')
        self._stmt_parts.append(', '.join(columns))
        self._stmt_parts.append('FROM')
        self._stmt_parts.append(self.table)
        self._stmt_parts.append('WHERE')
        self._stmt_parts.append(self.deleted_time_column)
        self._stmt_parts.append('= 0')

        result = self.where(conditions)
        if isinstance(result, Error):
            return result

        if order_by != '':
            self._stmt_parts.append('ORDER BY')
            self._stmt_parts.append(order_by)
            self._stmt_parts.append('ASC' if is_asc else 'DESC')

        self._stmt_parts.append('LIMIT %s OFFSET %s')
        self._params.append(limit)
        self._params.append(offset)

        stmt = ' '.join(self._stmt_parts)
        cursor = connections[self.database].cursor()

        try:
            cursor.execute(stmt, self._params)
            result = [row_to_dict(cursor, row) for row in cursor.fetchall()]
        except Error as error:
            result = error
        finally:
            cursor.close()

        return result

    def update(self, values, conditions):
        self.clear()

        column_equal_value = []
        for k, v in values.items():
            column_equal_value.append(k + ' = %s')
            self._params.append(v)

        self._stmt_parts.append('UPDATE')
        self._stmt_parts.append(self.table)
        self._stmt_parts.append('SET')
        self._stmt_parts.append(', '.join(column_equal_value))
        self._stmt_parts.append('WHERE')
        self._stmt_parts.append(self.deleted_time_column)
        self._stmt_parts.append('= 0')

        result = self.where(conditions)
        if isinstance(result, Error):
            return result

        stmt = ' '.join(self._stmt_parts)
        cursor = connections[self.database].cursor()

        try:
            cursor.execute(stmt, self._params)
            result = cursor.rowcount
        except Error as error:
            result = error
        finally:
            cursor.close()

        return result

    def delete(self, conditions):
        self.clear()

        self._stmt_parts.append('UPDATE')
        self._stmt_parts.append(self.table)
        self._stmt_parts.append('SET')
        self._stmt_parts.append(self.deleted_time_column)
        self._stmt_parts.append('= %s WHERE')
        self._stmt_parts.append(self.deleted_time_column)
        self._stmt_parts.append('= 0')
        self._params.append(now_int())

        result = self.where(conditions)
        if isinstance(result, Error):
            return result

        stmt = ' '.join(self._stmt_parts)
        cursor = connections[self.database].cursor()

        try:
            cursor.execute(stmt, self._params)
            result = cursor.rowcount
        except Error as error:
            result = error
        finally:
            cursor.close()

        return result

    def describe(self):
        if settings.DEFAULT_DATABASE_ENGINE == 'sqlite3':
            stmt = 'PRAGMA table_info(' + self.table + ')'
        else:  # mysql
            stmt = 'DESCRIBE ' + self.table
        cursor = connections[self.database].cursor()

        try:
            cursor.execute(stmt, self._params)
            result = [row_to_dict(cursor, row) for row in cursor.fetchall()]
        except Error as error:
            result = error
        finally:
            cursor.close()

        return result


tables = {
    'Users': Table('api', 'Users', 'userId', '', 'insertTime', 'updateTime', 'deleteTime'),
}
