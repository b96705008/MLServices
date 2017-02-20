import shutil, os, csv

from basic.algorithm import MLAlgorithm
from utils.env import logger
from pyspark.mllib.recommendation import ALS

class MyRewardsALSTrain(MLAlgorithm):
    def train_model(self):
        logger.info('Training the ALS model...')
        self.model = ALS.train(self.dataset.rating_data,
                               rank = self.rank,
                               seed = self.seed,
                               iterations = self.iterations,
                               lambda_ = self.regularization_parameter)
        logger.info('ALS model built!')

    def save_model(self):
        logger.info("Saving the ALS model...")

        try:
            shutil.rmtree(self.model_path)
        except Exception:
            pass

        self.model.save(self.sc, "file:" + os.path.join(self.model_path, "als_model"))

        logger.info("Saving rating data and mapping table...")
        with open(os.path.join(self.model_path, "als_customer_map.csv"), "w") as f:
            output = csv.writer(f)
            output.writerows(self.dataset.customer_map.items())

        with open(os.path.join(self.model_path, "als_feature_map.csv"), "w") as f:
            output = csv.writer(f)
            for feature_id, feature_seq in self.dataset.feature_map.items():
                output.writerow([feature_id[0], feature_id[1], feature_seq])
