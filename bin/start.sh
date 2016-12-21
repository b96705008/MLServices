#!/bin/sh

BASEPATH=$(pwd)/../
CONF_REDIS=${BASEPATH}/redis/ml_service.conf

# Export PYTHONPATH
export PYTHONPATH=$PYTHONPATH:${BASEPATH}

# Start the redis server
redis-server ${CONF_REDIS}
