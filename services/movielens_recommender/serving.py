from utils.env import root_dir, nice_json, init_spark_context
from flask import Flask, Blueprint, request
from engine import MovieRCEngine
import redis

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_engine(sc):
    movie_path = "{}/datasets/ml-latest-small/movies.csv".format(root_dir())
    model_path = "{}/models/movie_lens_als".format(root_dir())
    r = redis.Redis()
    engine = MovieRCEngine(sc, model_path, movie_path, r)
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
    engine = init_engine(sc)
    engine.start()
    service = get_service(engine)
    app = Flask(__name__)
    app.register_blueprint(service)
    app.run(port=5002, debug=True)
