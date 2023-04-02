#!/bin/sh

sudo systemctl enable gunicorn.service

sudo systemctl daemon-reload
sudo systemctl restart gunicorn.service

sudo systemctl status gunicorn.service