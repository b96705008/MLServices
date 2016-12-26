#!/bin/sh

BASEPATH=$(pwd)

LIB_PYTHON=${BASEPATH}/lib
LIB_REDIS=${BASEPATH}/etc/redis
CONF_REDIS=ml_service.conf

# Export PYTHONPATH
export PYTHONPATH=$PYTHONPATH:${LIB_PYTHON}

# Start the redis server
PID_FILE_REDIS=$(grep "pidfile" ${LIB_REDIS}/${CONF_REDIS} | awk '{print $2}')
if [ ! -e ${PID_FILE_REDIS} ]; then
    cd ${LIB_REDIS}
    redis-server ${CONF_REDIS}
fi
