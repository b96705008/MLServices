#!/usr/bin/env python

import os
import click

from flask import Flask

from utils.env import root_dir

options = {"iris": {"class_dataset": "IrisDataset",
                    "class_algo": "IrisDNN",
                    "class_builder": "IrisBuilder",
                    "class_engine": "IrisEngine",
                    "class_model": "IrisModel",
                    "dataset": "iris.csv",
                    "model": "iris_dnn",
                    "location": "iris_classifier",
                    "channel_builder": "iris_builder",
                    "channel_api": "iris_api"}}

@click.command()
@click.option("-s", "--service", required=True)
@click.option("-f", "--func", type=click.Choice(["builder", "api"]))
@click.option("-p", "--port", default=5001)
@click.option("-v", "--debug", default=False)
def run(service, func, port, debug):
    service_name = options[service]["location"]

    dataset_path = os.path.join(root_dir(), "datasets", options[service]["dataset"])
    model_path = os.path.join(root_dir(), "models", options[service]["model"])

    mod = __import__("services.{}.builder.dataset".format(service_name),
                     fromlist=["services.{}.builder".format(service_name)])
    class_dataset = getattr(mod, options[service]["class_dataset"])

    mod = __import__("services.{}.builder.algorithm".format(service_name),
                     fromlist=["services.{}.builder".format(service_name)])
    class_algo = getattr(mod, options[service]["class_algo"])

    mod = __import__("services.{}.api.model".format(service_name),
                     fromlist=["services.{}.api".format(service_name)])
    class_model = getattr(mod, options[service]["class_model"])

    channel_builder = options[service]["channel_builder"]
    channel_api = options[service]["channel_api"]
    channels = [channel_builder, channel_api]   # channels[0]: for Builder, channels[1]: after building model, inform whom

    # start service
    if func == 'builder':
        # import dynamic modules
        builder = __import__("services.{}.builder.builder".format(service_name),
                             fromlist=["services.{}.builder".format(service_name)])

        tbuilder = getattr(builder, options[service]["class_builder"])(class_dataset, dataset_path, class_algo, model_path, channels)
        tbuilder.build()
        tbuilder.run()

    elif func == 'api':
        # import dynamic modules
        engine = __import__("services.{}.api.engine".format(service_name),
                             fromlist=["services.{}.engine".format(service_name)])

        tengine = getattr(engine, options[service]["class_engine"])(dataset_path, class_model, model_path, [channel_api])
        tengine.run()

        mod = __import__("services.{}.api.service".format(service_name),
                         fromlist=["services.{}.service".format(service_name)])
        service = mod.get_service(tengine, service_name = options[service]["location"])

        app = Flask(service)
        app.register_blueprint(service)
        app.run(port=port, debug=debug)

if __name__ == "__main__":
    run()
