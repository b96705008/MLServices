import uuid

from utils.env import logger, sc
from basic.engine import MLEngine


class MyRewardsCBEngine(MLEngine):
    def refresh_model(self):
        logger.info("refresh {} model ...".format(type(self).__name__))

        # service
        params = {"_id": str(uuid.uuid1()),
                  "sc": sc,
                  "model_path": self.model_path}

        self.model = self.class_model(params)
