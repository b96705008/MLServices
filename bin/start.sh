#!/bin/sh

BASEPATH=$(pwd)/../
CONF_REDIS=${BASEPATH}/redis/ml_service.conf

# Export PYTHONPATH
export PYTHONPATH=$PYTHONPATH:${BASEPATH}

# Start the redis server
PID_FILE_REDIS=$(grep "pidfile" ${CONF_REDIS} | awk '{print $2}')
#if [ ! -e ${PID_FILE_REDIS} ]; then
redis-server ${CONF_REDIS}
#fi
