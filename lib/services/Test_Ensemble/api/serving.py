from utils.env import nice_json, logger
from flask import Blueprint, request


def get_service(service_name, engines):
    service = Blueprint(service_name, __name__)

    def parse_feature_str(feature_str):
        return map(lambda x: float(x), feature_str.split(","))

    @service.route("/<string:model>/<string:user_id>/<int:count>", methods=['GET'])
    def hello(model, user_id, count):
        params = {"model" : model,
                  "user_id": user_id,
                  "count": count}

        for model_name, engine in engines:
            if model_name == "MyRewards_ALS":
                MyRewards_ALS_result = engine.get_model().get_top_ratings(params)
            elif model_name == "MyRewards_CB":
                MyRewards_CB_result = engine.get_model().get_top_ratings(params)

        if model == "ALS":
            results = MyRewards_ALS_result
        elif model == "CB":
            results = MyRewards_CB_result
        elif model == "ALL":
            results = [MyRewards_ALS_result, MyRewards_CB_result]
        else:
            results = "something wrong, please check..."

        return nice_json(results)

    return service


