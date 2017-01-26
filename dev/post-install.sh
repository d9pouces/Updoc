#!/bin/sh

set -e

USER_EXISTS=`getent passwd updoc || :`
if [ -z "${USER_EXISTS}" ]; then
    useradd updoc -b /var/ -U -r
fi


mkdir -p /opt/updoc/var/media
mkdir -p /opt/updoc/var/data
mkdir -p /opt/updoc/var/log
chown -R : /opt/updoc


set +e

