#!/usr/bin/env python

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "lib"))

import click
import socket
import ConfigParser

from threading import Thread
from flask import Flask
from utils.env import root_dir, data_dir, get_ip, init_spark_context, logger

@click.command()
@click.option("-s", "--service", required=True)
@click.option("-f", "--func", type=click.Choice(["mining", "api"]))
@click.option("-v", "--debug", default=False)
def run(service, func, debug):
    basepath = os.path.join(data_dir(), service)
    filepath_cfg = os.path.join(basepath, "{}.cfg".format(func))

    cfg = ConfigParser.RawConfigParser()
    cfg.read(filepath_cfg)

    service_name = cfg.get("path", "location")

    model_path = os.path.join(basepath, "model", cfg.get("path", "model"))

    if cfg.has_option("setting", "spark_mode") and cfg.getboolean("setting", "spark_mode"):
        init_spark_context()
        logger.info("Turn on the spark_mode")

    listener = None

    # start service
    if func == 'mining':
        dataset_builder_path = os.path.join(basepath, "dataset", cfg.get("path", "dataset_builder"))

        mod = __import__("services.{}.mining.dataset".format(service_name), fromlist=["services.{}.mining".format(service_name)])
        class_dataset = getattr(mod, cfg.get("class", "dataset"))

        mod = __import__("services.{}.mining.algorithm".format(service_name), fromlist=["services.{}.mining".format(service_name)])
        class_algo = getattr(mod, cfg.get("class", "algorithm"))

        channel_builder = cfg.get("channel", "mining")
        channel_api = cfg.get("channel", "api")
        channels = [channel_builder, channel_api]   # channels[0]: for Builder, channels[1]: after building model, inform whom

        # import dynamic modules
        builder = __import__("services.{}.api.builder".format(service_name), fromlist=["services.{}.api".format(service_name)])
        tbuilder = getattr(builder, cfg.get("class", "builder"))(class_dataset, dataset_builder_path, class_algo, model_path,\
                           channels=channels, listener=listener)
        tbuilder.build()
        tbuilder.run()

    elif func == 'api':
        dataset_api_path = os.path.join(basepath, "dataset", cfg.get("path", "dataset_api"))
        channel_api = cfg.get("channel", "api")

        mod = __import__("services.{}.common.model".format(service_name), fromlist=["services.{}.common".format(service_name)])
        class_model = getattr(mod, cfg.get("class", "model"))

        # import dynamic modules
        engine = __import__("services.{}.api.engine".format(service_name), fromlist=["services.{}.api".format(service_name)])

        tengine = getattr(engine, cfg.get("class", "engine"))(dataset_api_path, class_model, model_path,\
                          channel=[channel_api], listener=listener)
        tengine.start()

        mod = __import__("services.{}.api.serving".format(service_name), fromlist=["services.{}.api".format(service_name)])
        service = mod.get_service(tengine, service_name)

        app = Flask(service_name)
        app.register_blueprint(service)

        port = cfg.getint("setting", "port")
        app.run(host=get_ip(), port=port, debug=debug)
    else:
        raise NotImplementedError

if __name__ == "__main__":
    run()
