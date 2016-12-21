#!/usr/bin/env python

import os
import sys
import redis
import click

from flask import Flask

from utils.env import root_dir, init_spark_context
from api.engine import MovieRCEngine
from api.serving import get_service
from builder.builder import MovieRCBuilder

@click.command()
@click.option("--channels", required=True)
@click.option("--service", type=click.Choice(["builder", "api"]))
def run(channels, service):
    sc = init_spark_context()

    module_name = __name__
    service_name = 'movie_lens_als'

    rating_path = "{}/datasets/ml-latest-small/ratings.csv".format(root_dir())
    movie_path = "{}/datasets/ml-latest-small/movies.csv".format(root_dir())
    model_path = "{}/models/movie_lens_als".format(root_dir())
    r = redis.Redis()

    # start service
    if service == 'builder':
        builder = MovieRCBuilder(sc, rating_path, model_path, channels=channels.split(","))
        builder.build_model()
        builder.run()

    elif service == 'api':
        engine = MovieRCEngine(sc, movie_path, model_path, channels=channels.split(","))
        engine.run()

        service = get_service(engine)

        app = Flask(__name__)
        app.register_blueprint(service)
        app.run(port=5002, debug=False)

if __name__ == "__main__":
    run()
