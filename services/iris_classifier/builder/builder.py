from basic.interface import MLBuilder

from dataset import IrisDataset
from algorithm import IrisDNN


class IrisModelBuilder(MLBuilder):
    def build_model(self):
        print("build iris model... ")
        # load dataset
        self.dataset = IrisDataset(self.dataset_path)

        # train model
        iris_dnn = IrisDNN(self.dataset, self.model_path)
        iris_dnn.train_model()
        iris_dnn.save_model()
