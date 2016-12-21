#!/usr/bin/env python

import os
import sys

import click
import redis

from flask import Flask

from api.serving import get_service
from api.serving import IrisPredictEngine
from builder.builder import IrisModelBuilder
from utils.env import root_dir

@click.command()
@click.option("--channels", required=True)
@click.option("--service", type=click.Choice(["builder", "api"]))
def run(channels, service):
    module_name = __name__
    service_name = 'iris_classifier'

    data_path = os.path.join(root_dir(), "datasets", "iris.csv")
    model_path = os.path.join(root_dir(), "models", "iris_dnn")

    # start service
    if service == 'builder':
        iris_builder = IrisModelBuilder(data_path, model_path, redis.Redis())
        iris_builder.build_model()
        iris_builder.run()

    elif service == 'api':
        engine = IrisPredictEngine(data_path, model_path, channels=channels.split(","))
        engine.start()

        service = get_service(engine, service_name)

        app = Flask(module_name)
        app.register_blueprint(service)
        app.run(port=5001, debug=False)

if __name__ == "__main__":
    run()
