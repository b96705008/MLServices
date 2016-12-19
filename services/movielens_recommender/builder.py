from dataset import MovieLenRatings
from algorithm import MovieALS
from model import MovieCFModel
from utils.env import root_dir, init_spark_context
import redis


# Maybe use luigi
class MovieRCBuilder:
    channel = 'movie_rc_builder'

    def __init__(self, sc, rating_path, model_path, r):
        self.sc = sc
        self.rating_path = rating_path
        self.model_path = model_path
        # redis channel
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe([self.channel])

    def refresh_dataset(self, new_dataset=None):
        print("refresh dataset ...")
        # dataset
        if new_dataset is None:
            self.dataset = MovieLenRatings(self.sc, self.rating_path)
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

        # publish
        self.redis.publish('movie_rc_api', 'NEW_MODEL')

    def refresh(self, train=True):
        print("refresh...")
        self.refresh_dataset()
        if train:
            self.refresh_model()
        else:
            self.model = MovieCFModel(self.sc, self.model_path, self.dataset_path)


    def run(self):
        print("\nListen build movie rc command...")
        for item in self.pubsub.listen():
            if item['data'] == 'KILL':
                self.pubsub.unsubscribe()
                print(self, 'unsubscribed and finished')
                break
            elif item['data'] == 'BUILD_MODEL':
                self.refresh(train=True)


if __name__ == '__main__':
    sc = init_spark_context()
    rating_path = "{}/datasets/ml-latest-small/ratings.csv".format(root_dir())
    model_path = "{}/models/movie_lens_als".format(root_dir())
    r = redis.Redis()
    builder = MovieRCBuilder(sc, rating_path, model_path, r)
    builder.refresh(train=True)
    builder.run()
