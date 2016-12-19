from dataset import IrisDataset
from algorithm import IrisDNN
from utils.env import root_dir
import redis


class IrisModelBuilder:
    channel = 'iris_builder'

    def __init__(self, dataset_path, model_path, r):
        self.dataset_path = dataset_path
        self.model_path = model_path
        # redis channel
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe([self.channel])

    def build_model(self):
        print("build iris model... ")
        # load dataset
        self.dataset = IrisDataset(self.dataset_path)

        # train model
        iris_dnn = IrisDNN(self.dataset, self.model_path)
        iris_dnn.train_model()
        iris_dnn.save_model()

        # publish
        self.redis.publish('iris_api', 'NEW_MODEL')

    def run(self):
        print("Listen build iris model command...")
        for item in self.pubsub.listen():
            if item['data'] == 'KILL':
                self.pubsub.unsubscribe()
                print(self, 'unsubscribed and finished')
                break
            elif item['data'] == 'BUILD_MODEL':
                self.build_model()


if __name__ == '__main__':
    dataset_path = "{}/datasets/iris.csv".format(root_dir())
    model_path = "{}/models/iris_dnn".format(root_dir())
    r = redis.Redis()
    builder = IrisModelBuilder(dataset_path, model_path, r)
    builder.build_model()
    builder.run()
