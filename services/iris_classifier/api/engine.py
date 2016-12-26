from basic.engine import MLEngine
from utils.env import logger

class IrisEngine(MLEngine):
    def refresh_model(self):
        logger.info("refresh iris model... ")

        params = {"model_path": self.model_path}
        self.model = self.class_model(params)
