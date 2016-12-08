import copy
from dataset import MovieLenDataset
from algorithm import MovieALS
from model import MovieCFModel

# Maybe use luigi
class MovieRCEngine:
    def __init__(self, sc, dataset_path, model_path):
        self.sc = sc
        self.dataset_path = dataset_path
        self.model_path = model_path
        ### some refresh scheduler

    def refresh_dataset(self, new_dataset=None):
        print("refresh dataset ...")
        # dataset
        if new_dataset is None:
            self.dataset = MovieLenDataset(self.sc, self.dataset_path)
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

        # service
        self.model = MovieCFModel(self.sc, self.model_path, self.dataset)

    def refresh(self, train=True):
        print("refresh...")
        self.refresh_dataset()
        if train:
            self.refresh_model()
        else:
            self.model = MovieCFModel(self.sc, self.model_path, self.dataset)

    def add_ratings(self, ratings, refresh=False):
        print('add ratings ...')
        self.dataset.add_ratings(ratings)
        if refresh:
            self.refresh_model()

    def get_model(self):
        #return copy.copy(self.model)
        return self.model
