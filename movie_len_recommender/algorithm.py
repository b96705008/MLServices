import os
import shutil
from pyspark.mllib.recommendation import ALS

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieALS:
    def __init__(self, sc, dataset, params):
        self.sc = sc
        self.dataset = dataset
        self.rank = params['rank']
        self.seed = params['seed']
        self.iterations = params['iterations']
        self.regularization_parameter = params['regularization_parameter']
        self.model_path = params['model_path']

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
