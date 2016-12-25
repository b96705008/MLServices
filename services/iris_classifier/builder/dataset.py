import pandas as pd

from basic.interface import MLDataset


class IrisDataset(MLDataset):
    def init(self):
        pass

    def prepare_data(self):
        iris = pd.read_csv(self.dataset_path)
        self.X = iris.values[:, :4]
        self.Y = iris.values[:, 4]
