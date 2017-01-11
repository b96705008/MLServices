from flask import Blueprint

from utils.env import nice_json

def get_service(engine, service_name):
    service = Blueprint(service_name, __name__)

    def parse_feature_str(feature_str):
        return map(lambda x: float(x), feature_str.split(","))

    @service.route("/features/<feature_str>/probs")
    def get_iris_probs(feature_str):
        features = parse_feature_str(feature_str)
        params = {"x": features}

        probs = engine.get_model().predict_probs(params)

        return nice_json(probs)

    @service.route("/features/<feature_str>/class")
    def get_iris_class(feature_str):
        features = parse_feature_str(feature_str)
        params = {"x": features}

        iris_class = engine.get_model().predict_class(params)

        return nice_json({'iris_class': iris_class})

    return service
