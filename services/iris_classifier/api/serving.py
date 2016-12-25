from flask import Blueprint

from utils.env import nice_json

def get_service(engine, service_name='iris_classifier'):
    service = Blueprint(service_name, __name__)

    def parse_feature_str(feature_str):
        return map(lambda x: float(x), feature_str.split(","))

    @service.route("/features/<feature_str>/probs")
    def get_iris_probs(feature_str):
        features = parse_feature_str(feature_str)
        dnn_clf = engine.get_model()
        probs = dnn_clf.predict_probs(features)

        return nice_json(probs)

    @service.route("/features/<feature_str>/class")
    def get_iris_class(feature_str):
        features = parse_feature_str(feature_str)
        dnn_clf = engine.get_model()
        iris_class = dnn_clf.predict_class(features)

        return nice_json({'iris_class': iris_class})

    return service
