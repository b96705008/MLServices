from basic.interface import MLEngine
from model import MovieCFModel

class MovieRCEngine(MLEngine):
    def __init__(self, sc, dataset_path, model_path, channels=[], listener=None):
        self.sc = sc

        MLEngine.__init__(self, dataset_path, model_path, channels, listener)

    def refresh_model(self):
        print("refresh model ...")
        # service
        self.model = MovieCFModel(self.sc, self.model_path, self.dataset_path)