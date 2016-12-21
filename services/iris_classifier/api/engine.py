from basic.interface import MLEngine
from model import IrisDnnClassifier

class IrisPredictEngine(MLEngine):
    def refresh_model(self):
        print("refresh iris model... ")

        self.model = IrisDnnClassifier(self.model_path)
