import os
from env import init_spark_context
from pyspark import SparkContext, SparkConf
from flask import Flask
from movie_len_recommender.serving import get_service, init_engine


if __name__ == '__main__':
        sc = init_spark_context()
        engine = init_engine(sc)
        movie_rc_service = get_service(engine)
        app = Flask(__name__)
        app.register_blueprint(movie_rc_service)
        app.run(port=5003, debug=True)
