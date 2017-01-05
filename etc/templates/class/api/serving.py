from utils.env import nice_json, logger
from flask import Blueprint, request

def get_service(engine, service_name):
    service = Blueprint(service_name, __name__)

    return service
