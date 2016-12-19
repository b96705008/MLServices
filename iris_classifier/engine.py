import threading
from dataset import IrisDataset
from algorithm import IrisDNN
from model import IrisDnnClassifier


class IrisPredictEngine(threading.Thread):
    channel = 'iris_api'
    model = None

    def __init__(self, dataset_path, model_path, r):
        self.dataset_path = dataset_path
        self.model_path = model_path
        # redis channel
        threading.Thread.__init__(self)
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe([self.channel])

    # def refresh_model(self):
    #     # load dataset
    #     self.dataset = IrisDataset(self.dataset_path)
    #
    #     # train model
    #     iris_dnn = IrisDNN(self.dataset, self.model_path)
    #     iris_dnn.train_model()
    #     iris_dnn.save_model()
    #
    #     # load model
    #     self.model = IrisDnnClassifier(self.model_path)
    #
    # def refresh(self, train=True):
    #     print("refresh IrisPredictEngine ... ")
    #     if train:
    #         self.refresh_model()
    #     else:
    #         self.model = IrisDnnClassifier(self.model_path)

    def refresh_model(self):
        print("refresh iris model... ")
        # load model
        self.model = IrisDnnClassifier(self.model_path)

    def get_model(self):
        return self.model

    def run(self):
        print("Run IrisPredictEngine thread...")
        for item in self.pubsub.listen():
            if item['data'] == 'KILL':
                self.pubsub.unsubscribe()
                print(self, 'unsubscribed and finished')
                break
            elif item['data'] == 'NEW_MODEL':
                self.refresh_model()
