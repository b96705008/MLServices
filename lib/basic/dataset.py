from utils.env import logger


class MLDataset(object):
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path

        self.init()
        self.prepare_data()

    def init(self):
        raise NotImplementedError

    def prepare_data(self):
        raise NotImplementedError
