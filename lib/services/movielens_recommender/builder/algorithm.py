import shutil

from basic.algorithm import MLAlgorithm
from utils.env import logger
from pyspark.mllib.recommendation import ALS

class MovieALS(MLAlgorithm):
    def train_model(self):
        logger.info('Training the ALS model...')
        self.model = ALS.train(self.dataset.ratings_RDD,
                               self.rank,
                               seed=self.seed,
                               iterations=self.iterations,
                               lambda_=self.regularization_parameter)
        logger.info('ALS model built!')

    def save_model(self):
        logger.info('Save model...')

        try:
            shutil.rmtree(self.model_path)
        except Exception:
             pass

        self.model.save(self.sc, self.model_path)
