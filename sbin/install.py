#!/usr/bin/env python

import os
import re
import shutil
import click

from utils.env import logger

SERVICE = "#SERVICE#"

def sed(filepath, service, capitalize=False):
    global SERVICE

    with open(filepath, "r") as sources:
        lines = sources.readlines()

    with open(filepath, "w") as sources:
        for line in lines:
            sources.write(re.sub(SERVICE, service.capitalize() if capitalize else service, line))

    logger.info("Replace #SERVICE# with {} for {}".format(service.capitalize() if capitalize else service, filepath))

@click.command()
@click.option("-s", "--service", required=True)
@click.option("-a", "--action", type=click.Choice(["install"]))
def main(action, service):
    basepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    template_path = os.path.join(basepath, "etc", "templates")

    cfg_path = os.path.join(template_path, "cfg")
    class_path = os.path.join(template_path, "class")

    target_cfg_path = os.path.join(basepath, "etc", service.lower())
    target_class_path = os.path.join(basepath, "lib", "services", service.lower())

    if action == "install":
        if not os.path.exists(target_cfg_path):
            shutil.copytree(cfg_path, target_cfg_path)
            logger.info("copy {} to {} successfully".format(cfg_path, target_cfg_path))
        else:
            logger.warn("{} is NOT empty".format(target_cfg_path))

        for filename in os.listdir(target_cfg_path):
            filepath = os.path.join(target_cfg_path, filename)
            if os.path.isfile(filepath):
                sed(filepath, service, False)

        if not os.path.exists(target_class_path):
            shutil.copytree(class_path, target_class_path)
            logger.info("copy {} to {} successfully".format(class_path, target_class_path))
        else:
            logger.warn("{} is NOT empty".format(target_class_path))

        for folder in ["api", "common", "mining"]:
            for filename in os.listdir(os.path.join(target_class_path, folder)):
                filepath = os.path.join(target_class_path, folder, filename)
                if os.path.isfile(filepath):
                    sed(filepath, service, True)
    else:
        raise NotImplementedError

if __name__ == "__main__":
    main()
