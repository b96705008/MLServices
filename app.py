import os
from env import init_spark_context
from pyspark import SparkContext, SparkConf
from flask import Flask
from movielens_recommender import serving as movie_rc
from iris_classifier import serving as iris_clf


if __name__ == '__main__':
    # main app
    app = Flask(__name__)

    # movielens recommendation service
    print("movielens recommender...")
    sc = init_spark_context()
    movie_engine = movie_rc.init_engine(sc, train = False)
    movie_rc_service = movie_rc.get_service(movie_engine)
    app.register_blueprint(movie_rc_service, url_prefix='/movielens')

    # iris classifier service
    print("iris classifier...")
    iris_engine = iris_clf.init_engine(train = False)
    iris_service = iris_clf.get_service(iris_engine)
    app.register_blueprint(iris_service, url_prefix='/iris')

    # start main server
    app.run(port=8000, debug=True)
