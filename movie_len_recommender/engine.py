from dataset import MovieLenDataset
from algorithm import MovieALS
from service import MovieCFService

# Maybe use luigi
class MovieRCEngine:
    def __init__(self, sc, dataset_path, model_path):
        self.sc = sc
        self.dataset_path = dataset_path
        self.model_path = model_path
        self.refresh_dataset()
        ### some refresh scheduler
        # self.refresh_dataset()
        # self.refresh_service()

    def refresh_dataset(self, new_dataset=None):
        # dataset
        if new_dataset is None:
            self.dataset = MovieLenDataset(self.sc, self.dataset_path)
        else:
            self.dataset = new_dataset

    def add_ratings(self, ratings):
        print('add ratings ...')
        self.dataset.add_ratings(ratings)

    def build_service(self):
        print("refresh service ...")
        print("rating count: " + str(self.dataset.ratings_RDD.count()))

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
        return MovieCFService(self.sc, self.model_path, self.dataset)
