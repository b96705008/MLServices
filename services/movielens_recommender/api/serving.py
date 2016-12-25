from utils.env import nice_json, logger
from flask import Blueprint, request


def get_service(engine, service_name):
    service = Blueprint(service_name, __name__)

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


