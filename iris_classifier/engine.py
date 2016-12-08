from dataset import IrisDataset
from algorithm import IrisDNN
from model import IrisDnnClassifier


class IrisPredictEngine:
    def __init__(self, dataset_path, model_path):
        self.dataset_path = dataset_path
        self.model_path = model_path

    def refresh_model(self):
        # load dataset
        self.dataset = IrisDataset(self.dataset_path)

        # train model
        iris_dnn = IrisDNN(self.dataset, self.model_path)
        iris_dnn.train_model()
        iris_dnn.save_model()

        # load model
        self.model = IrisDnnClassifier(self.model_path)

    def refresh(self, train=True):
        if train:
            self.refresh_model()
        else:
            self.model = IrisDnnClassifier(self.model_path)

    def get_model(self):
        return self.model
