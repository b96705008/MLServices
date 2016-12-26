import os
import json

from flask import make_response
from pyspark import SparkContext, SparkConf

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sc = None

def root_dir():
    """ Returns root director for this project """
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "..")

def data_dir():
    return os.path.join(root_dir(), "etc")


def nice_json(arg):
    response = make_response(json.dumps(arg, sort_keys = True, indent=4))
    response.headers['Content-type'] = "application/json"
    return response


def init_spark_context():
    global sc

    conf = SparkConf().setAppName("ALS Service").setMaster("local[*]")
    sc = SparkContext(conf=conf)

    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org").setLevel(logger.Level.OFF)
    logger.LogManager.getLogger("akka").setLevel(logger.Level.OFF)
