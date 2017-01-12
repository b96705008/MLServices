from utils.env import nice_json, logger
from flask import Blueprint, request

##############################################
# 請根據需求，撰寫你的 service
##############################################

def get_service(service_name, engines):
    service = Blueprint(service_name, __name__)

    '''
    engines: list type, 可拿到所有的 model, 拿法是
    for model_name, engine in engines:
        model_name <-- model 名稱
        model <-- engine.get_model() 可拿取
    '''


    @service.route("", methods=['GET'])
    def hello():
        return "Hello World!"

    return service
