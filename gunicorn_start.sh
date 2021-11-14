#!/bin/sh
gunicorn --chdir app webhook_forwarder:application -w 2 -b 0.0.0.0:8000