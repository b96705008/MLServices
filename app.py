#!/usr/bin/env python

import os
import click
import ConfigParser

from flask import Flask
from utils.env import root_dir, init_spark_context, logger

@click.command()
@click.option("-c", "--config", required=True)
@click.option("-s", "--service", required=True)
@click.option("-f", "--func", type=click.Choice(["builder", "api"]))
@click.option("-p", "--port", default=5001)
@click.option("-v", "--debug", default=False)
def run(config, service, func, port, debug):
    cfg = ConfigParser.RawConfigParser()
    cfg.read(config)

    service_name = cfg.get("path", "location")

    dataset_api_path = os.path.join(root_dir(), "datasets", cfg.get("path", "dataset_api"))
    dataset_builder_path = os.path.join(root_dir(), "datasets", cfg.get("path", "dataset_builder"))
    model_path = os.path.join(root_dir(), "models", cfg.get("path", "model"))

    if cfg.has_option("setting", "spark_mode") and cfg.getboolean("setting", "spark_mode"):
        init_spark_context()
        logger.info("Turn on the spark_mode")

    listener = None

    mod = __import__("services.{}.builder.dataset".format(service_name),
                     fromlist=["services.{}.builder".format(service_name)])
    class_dataset = getattr(mod, cfg.get("class", "dataset"))

    mod = __import__("services.{}.builder.algorithm".format(service_name),
                     fromlist=["services.{}.builder".format(service_name)])
    class_algo = getattr(mod, cfg.get("class", "algorithm"))

    mod = __import__("services.{}.api.model".format(service_name),
                     fromlist=["services.{}.api".format(service_name)])
    class_model = getattr(mod, cfg.get("class", "model"))

    channel_builder = cfg.get("channel", "builder")
    channel_api = cfg.get("channel", "api")
    channels = [channel_builder, channel_api]   # channels[0]: for Builder, channels[1]: after building model, inform whom

    # start service
    if func == 'builder':
        # import dynamic modules
        builder = __import__("services.{}.builder.builder".format(service_name),
                             fromlist=["services.{}.builder".format(service_name)])

        tbuilder = getattr(builder, cfg.get("class", "builder"))(class_dataset, dataset_builder_path, class_algo, model_path,\
                           channels=channels, listener=listener)
        tbuilder.build()
        tbuilder.run()

    elif func == 'api':
        # import dynamic modules
        engine = __import__("services.{}.api.engine".format(service_name),
                             fromlist=["services.{}.engine".format(service_name)])

        tengine = getattr(engine, cfg.get("class", "engine"))(dataset_api_path, class_model, model_path,\
                          channel=[channel_api], listener=listener)
        tengine.run()

        mod = __import__("services.{}.api.service".format(service_name),
                         fromlist=["services.{}.service".format(service_name)])
        service = mod.get_service(tengine, service_name)

        app = Flask(service)
        app.register_blueprint(service)
        app.run(port=port, debug=debug)

if __name__ == "__main__":
    run()
