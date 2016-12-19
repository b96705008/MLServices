import numpy as np
from keras.models import model_from_json


class IrisDnnClassifier:
    def __init__(self, model_path):
        self.model_path = model_path
        self.load_model()

    def load_model(self):
        print("Loaded model from disk")

        # load json and create model
        json_file = open(self.model_path + "/iris_model.json", 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)

        # load weights into new model
        loaded_model.load_weights(self.model_path + "/model.h5")

        # warm up
        x = loaded_model.predict(np.array([[2,3,4,1]]))

        # setting
        self.model = loaded_model
        self.classes = np.load(self.model_path + "/classes.npy")

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
