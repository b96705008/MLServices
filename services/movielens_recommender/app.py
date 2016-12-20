import sys
from flask import Flask
import redis

from utils.env import root_dir, init_spark_context
from api.engine import MovieRCEngine
from api.serving import get_service
from builder.builder import MovieRCBuilder

if __name__ == '__main__':
    service_type = 'builder'
    sc = init_spark_context()
    rating_path = "{}/datasets/ml-latest-small/ratings.csv".format(root_dir())
    movie_path = "{}/datasets/ml-latest-small/movies.csv".format(root_dir())
    model_path = "{}/models/movie_lens_als".format(root_dir())
    r = redis.Redis()

    # sys args
    if len(sys.argv) > 1:
        service_type = sys.argv[1]

    # start service
    if service_type == 'builder':
        builder = MovieRCBuilder(sc, rating_path, model_path, r)
        builder.refresh()
        builder.run()

    elif service_type == 'api':
        engine = MovieRCEngine(sc, model_path, movie_path, r)
        engine.start()
        service = get_service(engine)
        app = Flask(__name__)
        app.register_blueprint(service)
        app.run(port=5002, debug=False)



