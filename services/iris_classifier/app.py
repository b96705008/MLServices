import sys

import redis
from flask import Flask

from api.serving import get_service
from api.serving import IrisPredictEngine
from builder.builder import IrisModelBuilder
from utils.env import root_dir

if __name__ == '__main__':
    service_type = 'builder'
    data_path = "{}/datasets/iris.csv".format(root_dir())
    model_path = "{}/models/iris_dnn".format(root_dir())
    r = redis.Redis()

    # sys args
    if len(sys.argv) > 1:
        service_type = sys.argv[1]

    # start service
    if service_type == 'builder':
        iris_builder = IrisModelBuilder(data_path, model_path, r)
        iris_builder.build_model()
        iris_builder.run()

    elif service_type == 'api':
        engine = IrisPredictEngine(data_path, model_path, r)
        engine.start()
        service = get_service(engine)
        app = Flask(__name__)
        app.register_blueprint(service)
        app.run(port=5001, debug=False)



