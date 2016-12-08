import os
from env import root_dir, nice_json, init_spark_context
from flask import Flask, Blueprint
from werkzeug.exceptions import NotFound
from movielens_recommender.engine import MovieRCEngine

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_engine(sc, train=True):
    dataset_path = "{}/datasets/ml-latest-small".format(root_dir())
    model_path = "{}/models/movie_lens_als".format(root_dir())
    engine = MovieRCEngine(sc, dataset_path, model_path)
    engine.refresh(train)
    return engine


def get_service(engine):
    service = Blueprint('movielens_recommender', __name__)

    @service.route("/users/<int:user_id>/top/<int:count>", methods=['GET'])
    def top_ratings(user_id, count):
        logger.debug("User %s TOP ratings requested", user_id)
        model = engine.get_model()
        top_ratings = model.get_top_ratings(user_id, count)
        return nice_json(top_ratings)


    @service.route("/users/<int:user_id>/ratings", methods=['POST'])
    def add_ratings(user_id):
        ratings_list = list(request.form.keys())[0].strip().split("\n")
        ratings_list = map(lambda x: x.split(","), ratings_list)
        ratings = map(lambda x: (user_id, int(x[0]), float(x[1])), ratings_list)
        engine.add_ratings(ratings, refresh=False)
        return nice_json(top_ratings), 201

    return service


if __name__ == '__main__':
    sc = init_spark_context()
    engine = init_engine(sc, False)
    service = get_service(engine)
    app = Flask(__name__)
    app.register_blueprint(service)
    app.run(port=5003, debug=True)
