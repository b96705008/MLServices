from utils.env import nice_json, logger
from flask import Blueprint, request


def get_service(service_name, engines):
    service = Blueprint(service_name, __name__)

    def parse_feature_str(feature_str):
        return map(lambda x: float(x), feature_str.split(","))

    @service.route("/<feature>/<int:user_id>/<int:count>", methods=['GET'])
    def hello(feature, user_id, count):
        results = []

        for model_name, engine in engines:
            if model_name == "iris":
                param = {"x": parse_feature_str(feature)}

                prob = engine.get_model().predict_probs(param)
                results.append(prob)
            elif model_name == "movielens":
                params = {"user_id": user_id, "count": count}

                top_rating = engine.get_model().get_top_ratings(params)

                results.append(top_rating)

        return nice_json(results)

    return service


