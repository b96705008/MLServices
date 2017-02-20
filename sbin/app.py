#!/usr/bin/env python

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "lib"))

import click
import socket
import ConfigParser
import jaydebeapi as jdbc

from threading import Thread
from flask import Flask
from utils.env import root_dir, data_dir, get_ip, init_spark_context, logger

def get_api_engine(basepath, cfg, service_name, model_path, listener=None):
    dataset_api_path = os.path.join(basepath, "dataset", cfg.get("path", "dataset_api"))
    channel_api = cfg.get("channel", "api")

    mod = __import__("services.{}.common.model".format(service_name), fromlist=["services.{}.common".format(service_name)])
    class_model = getattr(mod, cfg.get("class", "model"))

    # import dynamic modules
    engine = __import__("services.{}.api.engine".format(service_name), fromlist=["services.{}.api".format(service_name)])
    tengine = getattr(engine, cfg.get("class", "engine"))(dataset_api_path, class_model, model_path,\
                      channel=[channel_api], listener=listener)

    return tengine

def get_api_service(cfg, service_name, tengine):
    mod = __import__("services.{}.api.serving".format(service_name), fromlist=["services.{}.api".format(service_name)])
    service = mod.get_service(tengine, service_name)

    return service

def get_mining_engine(connect_td, cfg, service_name, model_path, listener=None):
    
    mod = __import__("services.{}.mining.dataset".format(service_name), fromlist=["services.{}.mining".format(service_name)])
    class_dataset = getattr(mod, cfg.get("class", "dataset"))

    mod = __import__("services.{}.mining.algorithm".format(service_name), fromlist=["services.{}.mining".format(service_name)])
    class_algo = getattr(mod, cfg.get("class", "algorithm"))

    channel_builder = cfg.get("channel", "mining")
    channel_api = cfg.get("channel", "api")
    channels = [channel_builder, channel_api]   # channels[0]: for Builder, channels[1]: after building model, inform whom

    # import dynamic modules
    builder = __import__("services.{}.api.builder".format(service_name), fromlist=["services.{}.api".format(service_name)])
    tbuilder = getattr(builder, cfg.get("class", "builder"))(class_dataset, connect_td, class_algo, model_path,\
                       channels=channels, listener=listener)

    return tbuilder

def init_setting(cfg):
    ensemble_mode = False
    if cfg.has_option("setting", "ensemble"):
        ensemble_mode = bool(cfg.get("setting", "ensemble"))

    service_name = cfg.get("setting", "service_name")
    port = cfg.getint("setting", "port")

    return ensemble_mode, service_name, port

def start_flask(service_name, service, cfg, port, debug):
    app = Flask(service_name)
    app.register_blueprint(service)

    port = cfg.getint("setting", "port")
    app.run(host=get_ip(), port=port, debug=debug)

@click.command()
@click.option("-s", "--service", required=True)
@click.option("-f", "--func", type=click.Choice(["mining", "api"]))
@click.option("-v", "--debug", default=False)
def run(service, func, debug):
    listener = None
    basepath = os.path.join(data_dir(), service)
    filepath_cfg = os.path.join(basepath, "{}.cfg".format(func))

    connect_td = "jdbc:teradata://<database_ip>/TMODE=TERA,CLIENT_CHARSET=WINDOWS-950,DATABASE=fh_temp,USER=<account>,PASSWORD=<password>"

    cfg = ConfigParser.RawConfigParser()
    cfg.read(filepath_cfg)

    ensemble_mode, service_name, port = init_setting(cfg)
    if cfg.has_option("setting", "spark_mode") and cfg.getboolean("setting", "spark_mode"):
        init_spark_context()
        logger.info("Turn on the spark_mode")

    # start service
    if ensemble_mode:
        if func == "mining":
            pass
        elif func == "api":
            idx, engines = 1, []

            section_name = "class{}".format(idx)
            while cfg.has_section(section_name):
                cfg_tmp = ConfigParser.RawConfigParser()
                cfg_tmp.read(cfg.get(section_name, "path"))

                _, t_service_name, port = init_setting(cfg_tmp)
                t_basepath = os.path.join(data_dir(), t_service_name)
                print t_basepath

                t_model_path = os.path.join(t_basepath, "model", cfg_tmp.get("path", "model"))
                print t_model_path

                t_engine = get_api_engine(t_basepath, cfg_tmp, t_service_name, t_model_path)
                t_engine.start()

                engines.append((t_service_name, t_engine))
                logger.info("Load {} model from {}".format(t_engine.model, t_model_path))

                idx += 1
                section_name = "class{}".format(idx)

            mod = __import__("services.{}.api.serving".format(service_name), fromlist=["services.{}.api".format(service_name)])
            service = mod.get_service(service_name, engines)

            start_flask(service_name, service, cfg, port, debug)
        else:
            raise NotImplementedError
    else:
        model_path = os.path.join(basepath, "model", cfg.get("path", "model"))

        if func == 'mining':
            tbuilder = get_mining_engine(connect_td, cfg, service_name, model_path, listener)
            tbuilder.build()
            tbuilder.run()

        elif func == 'api':
            tengine = get_api_engine(basepath, cfg, service_name, model_path, listener)
            tengine.start()

            service = get_api_service(cfg, service_name, tengine)
            start_flask(service_name, service, cfg, port, debug)
        else:
            raise NotImplementedError

if __name__ == "__main__":
    run()
