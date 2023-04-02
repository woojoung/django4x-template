#!/bin/sh

rm -rf ./django_collect_static
python3 ./manage.py collectstatic
mv ./django_collect_static /usr/share/nginx/html
