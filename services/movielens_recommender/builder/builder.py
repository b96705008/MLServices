from utils.env import logger, sc

from basic.builder import MLBuilder
from algorithm import MovieALS
from dataset import MovieLenRatings
from services.movielens_recommender.api.model import MovieCFModel


class MovieRCBuilder(MLBuilder):
    def refresh_dataset(self, new_dataset=None):
        logger.info("refresh dataset of {}...".format(type(self).__name__))

        # dataset
        if new_dataset is None:
            self.dataset = MovieLenRatings(self.dataset_path)
        else:
            self.dataset = new_dataset

    def refresh_model(self):
        logger.info("refresh {} model ...".format(type(self).__name__))

        # algorithm
        params = {'rank': 8,
                  'seed': 5,
                  'iterations': 10,
                  'regularization_parameter': 0.1,
                  'model_path': self.model_path,
                  'sc': sc,
                  'dataset': self.dataset
        }

        movie_rc_algo = MovieALS(params)

    def build_model(self):
        self.refresh_dataset()
        self.refresh_model()
