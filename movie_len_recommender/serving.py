import os
from movie_len_recommender.engine import MovieRCEngine
from env import root_dir, nice_json, init_spark_context
from flask import Flask
import json
from werkzeug.exceptions import NotFound

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask import Blueprint


def init_engine(sc):
    dataset_path = "{}/datasets/ml-latest-small".format(root_dir())
    model_path = "{}/models/movie_lens_als".format(root_dir())
    return MovieRCEngine(sc, dataset_path, model_path)


def get_service(engine):
    service = Blueprint('movie_len_recommender', __name__)

    @service.route("/<int:user_id>/ratings/top/<int:count>", methods=['GET'])
    def top_ratings(user_id, count):
        logger.debug("User %s TOP ratings requested", user_id)
        model = engine.get_model()
        top_ratings = model.get_top_ratings(user_id, count) #recommendation_engine.get_top_ratings(user_id,count)
        return nice_json(top_ratings)


    @service.route("/<int:user_id>/ratings", methods=['POST'])
    def add_ratings(user_id):
        ratings_list = list(request.form.keys())[0].strip().split("\n")
        ratings_list = map(lambda x: x.split(","), ratings_list)
        ratings = map(lambda x: (user_id, int(x[0]), float(x[1])), ratings_list)
        engine.add_ratings(ratings, refresh=True)
        return nice_json(top_ratings), 201

    return service


if __name__ == '__main__':
    sc = init_spark_context()
    engine = init_engine(sc)
    service = get_service(engine)
    app = Flask(__name__)
    app.register_blueprint(service)
    app.run(port=5003, debug=True)
