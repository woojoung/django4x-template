import json
from http import HTTPStatus
from http.client import HTTPSConnection, HTTPConnection
from django.conf import settings
from pytz import timezone
from datetime import datetime
import jwt
import ssl
from hashlib import md5
from types import SimpleNamespace
from urllib.parse import urlparse
import google.auth


def try_get_ints(ids):
    try:
        result = [str(int(s)) for s in ids]
    except ValueError as error:
        result = error

    return result


def now_str():
    return datetime.now(timezone(settings.DEFAULT_TIMEZONE)).strftime(settings.DEFAULT_DATETIME_FORMAT)


def now_int():
    return int(datetime.now(timezone(settings.DEFAULT_TIMEZONE)).strftime('%Y%m%d%H%M%S'))


def epoch_str():
    return datetime(1970, 1, 1, 0, 0, 0, 0, timezone(settings.DEFAULT_TIMEZONE)).strftime(
        settings.DEFAULT_DATETIME_FORMAT)


def try_jwt_decode(t):
    try:
        result = jwt.decode(t, settings.SECRET_KEY, algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
    except jwt.InvalidTokenError as error:
        result = error

    return result


def try_json_loads(s):
    try:
        result = json.loads(s)
    except ValueError as error:
        result = error

    return result


def mysql_type(t):
    if t == 0x00:
        return 'DECIMAL'
    elif t == 0x01:
        return 'TINY'
    elif t == 0x02:
        return 'SHORT'
    elif t == 0x03:
        return 'LONG'
    elif t == 0x04:
        return 'FLOAT'
    elif t == 0x05:
        return 'DOUBLE'
    elif t == 0x06:
        return 'NULL'
    elif t == 0x07:
        return 'TIMESTAMP'
    elif t == 0x08:
        return 'LONGLONG'
    elif t == 0x09:
        return 'INT24'
    elif t == 0x0a:
        return 'DATE'
    elif t == 0x0b:
        return 'TIME'
    elif t == 0x0c:
        return 'DATETIME'
    elif t == 0x0d:
        return 'YEAR'
    elif t == 0x0e:
        return 'NEWDATE'
    elif t == 0x0f:
        return 'VARCHAR'
    elif t == 0x10:
        return 'BIT'
    elif t == 0xf5:
        return 'JSON'
    elif t == 0xf6:
        return 'NEWDECIMAL'
    elif t == 0xf7:
        return 'ENUM'
    elif t == 0xf8:
        return 'SET'
    elif t == 0xf9:
        return 'TINY_BLOB'
    elif t == 0xfa:
        return 'MEDIUM_BLOB'
    elif t == 0xfb:
        return 'LONG_BLOB'
    elif t == 0xfc:
        return 'BLOB'
    elif t == 0xfd:
        return 'VAR_STRING'
    elif t == 0xfe:
        return 'STRING'
    elif t == 0xff:
        return 'GEOMETRY'
    else:
        return 'UNKNOWN'


# def row_to_dict(cursor, row):
#     _dict = {}
#     for i, column in enumerate(cursor.description):
#         _dict[column[0]] = row[i]
#         # print(mysql_type(column[1]))
#     return _dict


def row_to_dict(cursor, row):
    column_names = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(column_names, row)}


class MyHttpResponse:
    def __init__(self, http_conn=None):
        if http_conn is None:
            self.http_status = HTTPStatus.INTERNAL_SERVER_ERROR
            self.body = ''
            return

        resp = http_conn.getresponse()
        self.http_status = resp.status
        self.body = resp.read().decode('utf-8')
        http_conn.close()


def http_request(method, url, headers, body=None):
    # error = MyHttpResponse()
    #
    # if body is not None and not isinstance(body, str):
    #     error.body = json.dumps({'detail': 'body must be a str'})
    #     return error
    #
    # if method in ['POST', 'PUT'] and body is None:
    #     error.body = json.dumps({'detail': 'body is required'})
    #     return error
    # elif method in ['GET', 'DELETE'] and body is not None:
    #     error.body = json.dumps({'detail': 'body must be None'})
    #     return error

    url_parsed = urlparse(url)

    scheme = url_parsed.scheme
    host = str(url_parsed.hostname)
    port = url_parsed.port
    _url = url_parsed.path
    query = url_parsed.query

    if query != '':
        _url += '?' + query

    if scheme == 'https':
        http_conn = HTTPSConnection(host=host, port=port, timeout=settings.DEFAULT_HTTP_TIMEOUT_SECONDS,
                                    context=ssl.create_default_context())
    else:
        http_conn = HTTPConnection(host=host, port=port, timeout=settings.DEFAULT_HTTP_TIMEOUT_SECONDS)

    http_conn.request(method=method, url=_url, headers=headers, body=body)
    resp = MyHttpResponse(http_conn)
    http_conn.close()

    return resp


def send_slack_to_channel(text):
    url = 'https://hooks.slack.com:443' + settings.SLACK_PATH
    resp = http_request('POST', url, {'Content-Type': 'application/json; charset=utf-8'}, json.dumps({'text': text}))
    return resp.http_status == HTTPStatus.OK


def md5_hex_digest(s):
    return md5(s.encode()).hexdigest()


def json_to_object(s):
    try:
        result = json.loads(s, object_hook=lambda d: SimpleNamespace(**d))
    except ValueError as error:
        result = error

    return result


def send_push_to_token(token, title, body):
    google_auth = google.auth.load_credentials_from_file(settings.PURCHASE_GOOGLE_APIS_JSON, [
        'https://www.googleapis.com/auth/cloud-platform',
        'https://www.googleapis.com/auth/firebase.messaging'
    ])

    url = 'https://fcm.googleapis.com:443/v1/projects/' + settings.PUSH_PROJECT_ID + '/messages:send'
    resp = http_request('POST', url, {
        'Authorization': 'Bearer ' + google_auth.token,
        'ContentType': 'application/json; charset=utf-8',
    }, {
        # 'validation_only': validation_only,
        'message': {
            'token': token,
            'notification': {
                'title': title,
                'body': body,
            }
        }
    })

    return resp
