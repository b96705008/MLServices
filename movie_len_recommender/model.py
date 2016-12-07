import os
import uuid
from pyspark.mllib.recommendation import MatrixFactorizationModel
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieCFModel:
    def __init__(self, sc, model_path, dataset):
        self._id = str(uuid.uuid1())
        self.sc = sc
        self.model_path = model_path
        self.dataset = dataset
        # load model
        self.model = MatrixFactorizationModel.load(sc, model_path)

    def __predict_ratings(self, user_and_movie_RDD):
        predicted_RDD = self.model.predictAll(user_and_movie_RDD)
        predicted_rating_RDD = predicted_RDD.map(lambda x: (x.product, x.rating))
        predicted_rating_title_and_count_RDD = predicted_rating_RDD \
            .join(self.dataset.movies_titles_RDD) \
            .join(self.dataset.movies_rating_counts_RDD)
        # title, rating, count
        predicted_rating_title_and_count_RDD = \
            predicted_rating_title_and_count_RDD.map(lambda r: (r[1][0][1], r[1][0][0], r[1][1]))

        return predicted_rating_title_and_count_RDD

    def get_top_ratings(self, user_id, movies_count):
        """
            Recommends up to movies_count top unrated movies to user_id
        """
        # Get pairs of (userID, movieID) for user_id unrated movies
        user_unrated_movies_RDD = self.dataset.movies_RDD \
            .filter(lambda rating: not rating[1] == user_id) \
            .map(lambda x: (user_id, x[0]))

        # Get predicted ratings
        ratings = self.__predict_ratings(user_unrated_movies_RDD) \
            .filter(lambda r: r[2] >= 25) \
            .takeOrdered(movies_count, key=lambda x: -x[1])

        result = map(lambda x: {'movie_title': x[0], 'rating': x[1], 'count': x[2]}, ratings)

        return result
