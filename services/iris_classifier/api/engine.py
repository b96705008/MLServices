from basic.engine import MLEngine
from utils.env import logger

class IrisEngine(MLEngine):
    def refresh_model(self):
        logger.info("refresh iris model... ")

        self.model = self.class_model(self.model_path)
