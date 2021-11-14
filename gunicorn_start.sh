#!/bin/sh
gunicorn webhook_forwarder:application -w 2 -b 0.0.0.0:80