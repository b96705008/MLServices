from utils.env import logger
from basic.interface import MLEngine
from model import MovieCFModel


class MovieRCEngine(MLEngine):
    def refresh_model(self):
        logger.info("refresh {} model ...".format(type(self).__name__))

        # service
        self.model = MovieCFModel(self.model_path, self.dataset_path)
