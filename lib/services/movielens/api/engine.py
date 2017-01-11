import uuid

from utils.env import logger, sc
from basic.engine import MLEngine


class MovieRCEngine(MLEngine):
    def refresh_model(self):
        logger.info("refresh {} model ...".format(type(self).__name__))

        # service
        params = {"_id": str(uuid.uuid1()),
                  "sc": sc,
                  "movie_path": self.dataset_path,
                  "model_path": self.model_path}

        self.model = self.class_model(params)
