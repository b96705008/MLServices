import os

from basic.model import MLModel
from utils.env import logger, sc
from pyspark.mllib.recommendation import MatrixFactorizationModel


class MovieCFModel(MLModel):
    def load_model(self):
        # load model
        self.model = MatrixFactorizationModel.load(sc, self.model_path)
        self.__load_movies()

    def __load_movies(self):
        logger.info("Loading Movies data...")

        movies_file_path = self.movie_path
        movies_raw_RDD = self.sc.textFile(movies_file_path)
        movies_raw_data_header = movies_raw_RDD.take(1)[0]
        self.movies_RDD = movies_raw_RDD \
            .filter(lambda line: line != movies_raw_data_header) \
            .map(lambda line: line.split(",")) \
            .map(lambda tokens: (int(tokens[0]), tokens[1], tokens[2])) \

        self.movies_titles_RDD = self.movies_RDD.map(lambda x: (int(x[0]), x[1])).cache()

    def __predict_ratings(self, user_and_movie_RDD):
        predicted_RDD = self.model.predictAll(user_and_movie_RDD)
        predicted_rating_RDD = predicted_RDD.map(lambda x: (x.product, x.rating))
        predicted_title_rating_RDD = predicted_rating_RDD \
            .join(self.movies_titles_RDD)\
            .map(lambda x: (x[1][1], x[1][0]))

        return predicted_title_rating_RDD

    def get_top_ratings(self, params):
        """
            Recommends up to movies_count top unrated movies to user_id
        """
        # Get pairs of (userID, movieID) for user_id unrated movies
        user_id = params["user_id"]
        count = params["count"]


        user_unrated_movies_RDD = self.movies_RDD \
            .filter(lambda rating: not rating[1] == user_id) \
            .map(lambda x: (user_id, x[0]))

        # Get predicted ratings
        ratings = self.__predict_ratings(user_unrated_movies_RDD) \
            .takeOrdered(count, key=lambda x: -x[1])

        result = map(lambda x: {'movie_title': x[0], 'rating': x[1]}, ratings)

        return result
