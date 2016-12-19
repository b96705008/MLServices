import threading
from model import MovieCFModel

# Maybe use luigi
class MovieRCEngine(threading.Thread):
    channel = 'movie_rc_api'

    def __init__(self, sc, model_path, movie_path, r):
        self.sc = sc
        self.model_path = model_path
        self.movie_path = movie_path
        # redis channel
        threading.Thread.__init__(self)
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe([self.channel])

        self.refresh_model()


    def refresh_model(self):
        print("refresh model ...")
        # service
        self.model = MovieCFModel(self.sc, self.model_path, self.movie_path)

    def get_model(self):
        return self.model

    def run(self):
        print("Run MovieRCEngine thread...")
        for item in self.pubsub.listen():
            if item['data'] == 'KILL':
                self.pubsub.unsubscribe()
                print(self, 'unsubscribed and finished')
                break
            elif item['data'] == 'NEW_MODEL':
                self.refresh_model()
