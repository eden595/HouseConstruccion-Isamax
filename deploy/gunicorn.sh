#!/bin/bash

NAME="urbix"
DJANGODIR=$(dirname $(cd `dirname $0` && pwd))
DJANGODIR2=$(dirname $(dirname $(cd `dirname $0` && pwd)))
SOCKFILE=/tmp/gunicorn-urbix.sock
LOGDIR=${DJANGODIR}/logs/gunicorn.log
USER=root
GROUP=root
NUM_WORKERS=8
DJANGO_WSGI_MODULE=urbix.wsgi

rm -frv $SOCKFILE

cd $DJANGODIR

exec ${DJANGODIR2}/.venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --env DJANGO_SETTINGS_MODULE=urbix.production \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
  --log-file=$LOGDIR
