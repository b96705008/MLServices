import pandas as pd
import numpy as np


class IrisDataset:
    def __init__(self, dataset_path):
        print('Read iris dataset...')
        self.dataset_path = dataset_path
        self.prepare_data()

    def prepare_data(self):
        iris = pd.read_csv(self.dataset_path)
        self.features = iris.values[:, :4]
        self.label = iris.values[:, 4]
