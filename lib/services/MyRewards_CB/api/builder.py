from utils.env import logger, sc

from basic.builder import MLBuilder


class MyRewarsCBBuilder(MLBuilder):
    def refresh_dataset(self, new_dataset=None):
        logger.info("refresh dataset of {}...".format(type(self).__name__))

        # dataset
        if new_dataset is None:
            self.dataset = self.class_dataset(self.dataset_path)
        else:
            self.dataset = new_dataset

    def refresh_model(self):
        logger.info("refresh {} model ...".format(type(self).__name__))

        # algorithm
        params = {'model_path': self.model_path,
                  'sc': sc,
                  'dataset': self.dataset
        }

        movie_rc_algo = self.class_model(params)

    def build_model(self):
        self.refresh_dataset()
        self.refresh_model()
