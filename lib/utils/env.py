import os
import json
import subprocess

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

    conf = SparkConf().setAppName("MyRewards Service").setMaster("local[*]")
                      # .serMaster("yarn").set("saprk.driver.memory", "2G").set("spark.executor.core", "4").set("spark.executor.memory", "2G")
    sc = SparkContext(conf=conf)

    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org").setLevel(logger.Level.OFF)
    logger.LogManager.getLogger("akka").setLevel(logger.Level.OFF)

def get_ip():
    host = "127.0.0.1"

    get_ip = os.path.join(root_dir(), "bin", "get_ip.sh")

    ips = subprocess.check_output([get_ip], shell=True).strip().split("\n")
    for ip in ips:
        if not ip.startswith("127.") and not ip.startswith("192.") and not ip.startswith("10."):
            host = ip
            break
        elif ip.startswith("192."):
            host = ip
            break

    return host

if __name__ == "__main__":
    print get_ip()
