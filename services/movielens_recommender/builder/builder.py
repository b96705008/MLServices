from basic.interface import MLBuilder
from algorithm import MovieALS
from dataset import MovieLenRatings
from services.movielens_recommender.api.model import MovieCFModel


class MovieRCBuilder(MLBuilder):
    def __init__(self, sc, dataset_path, model_path, channels=[], listener=None):
        self.sc = sc
        MLBuilder.__init__(self, dataset_path, model_path, channels, listener)

    def refresh_dataset(self, new_dataset=None):
        print("refresh dataset ...")
        # dataset
        if new_dataset is None:
            self.dataset = MovieLenRatings(self.sc, self.dataset_path)
        else:
            self.dataset = new_dataset

    def refresh_model(self):
        print("refresh model ...")

        # algorithm
        movie_rc_algo = MovieALS(self.sc, self.dataset, {
            'rank': 8,
            'seed': 5,
            'iterations': 10,
            'regularization_parameter': 0.1,
            'model_path': self.model_path
        })
        movie_rc_algo.train_model()
        movie_rc_algo.save_model()

    def build_model(self):
        self.refresh_dataset()
        self.refresh_model()
