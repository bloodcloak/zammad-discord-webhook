FROM python:3.8-alpine

RUN adduser -D webhook
WORKDIR /home/webhook
COPY requirements.txt ./requirements.txt

RUN export PIP_NO_CACHE_DIR=false && apk update && apk add --update --no-cache --virtual .build-deps alpine-sdk
RUN pip3 install -r requirements.txt && rm -f requirements.txt
COPY webhook_forwarder.py ./webhook_forwarder.py
COPY gunicorn_start.sh ./gunicorn_start.sh

COPY --chown=webhook:webhook . .
USER webhook

EXPOSE 80
ENTRYPOINT [ "sh", "gunicorn_start.sh" ]