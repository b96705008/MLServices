import os
import numpy as np

from basic.model import MLModel
from utils.env import logger

from keras.models import model_from_json

class IrisModel(MLModel):
    def load_model(self):
        logger.info("Loaded model from disk")

        # load json and create model
        filepath = os.path.join(self.model_path, "iris_model.json")
        with open(filepath) as in_file:
            loaded_model_json = in_file.read()
            loaded_model = model_from_json(loaded_model_json)

        # load weights into new model
        filepath = os.path.join(self.model_path, "model.h5")
        loaded_model.load_weights(filepath)

        # warm up
        loaded_model.predict(np.array([[2,3,4,1]]))

        # setting
        self.model = loaded_model

        filepath = os.path.join(self.model_path, "classes.npy")
        self.classes = np.load(filepath)

    def __process_query(self, features):
        return np.array(features).reshape(-1, 4)

    def predict_probs(self, features):
        data = self.__process_query(features)
        probs = self.model.predict(data)[0]
        result = {}
        for idx, prob in enumerate(probs):
            result[self.classes[idx]] = float(prob)

        return result

    def predict_class(self, features):
        data = self.__process_query(features)
        class_idx = self.model.predict_classes(data)[0]

        return self.classes[class_idx]
