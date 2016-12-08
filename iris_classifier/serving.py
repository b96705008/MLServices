from env import root_dir, nice_json
from flask import Flask, Blueprint
import json
from engine import IrisPredictEngine

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_engine(train=True):
    dataset_path = "{}/datasets/iris.csv".format(root_dir())
    model_path = "{}/models/iris_dnn".format(root_dir())
    engine = IrisPredictEngine(dataset_path, model_path)
    engine.refresh(train)
    return engine


def get_service(engine):
    service = Blueprint('iris_classifier', __name__)

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

if __name__ == '__main__':
    engine = init_engine()
    service = get_service(engine)
    app = Flask(__name__)
    app.register_blueprint(service)
    app.run(port=5001, debug=True)

    # #iris_dnn_clf = IrisDnnClassifier(model_path)
    # print(iris_dnn_clf.predict_probs([2,3,4,1]))
    # print(iris_dnn_clf.predict_class([2,3,4,1]))
