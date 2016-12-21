import redis
import threading

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLListener(object):
    def __init__(self, r=None, channels=[]):
        if r is None:
            self.redis = redis.Redis()
        else:
            self.redis = r

        self.pubsub = self.redis.pubsub()

        if channels:
            self.subscribe(channels)

        self.channels = channels

    def get_channels(self):
        return self.channels

    def listen(self):
        for item in self.pubsub.listen():
            yield item

    def unsubscribe(self):
        self.pubsub.unsubscribe()
        logger.info('{} tries to unsubscribe the channelds successfully'.format(type(self).__name__))

    def subscribe(self, channels):
        self.pubsub.subscribe(channels)


class MLEngine(threading.Thread):
    def __init__(self, dataset_path, model_path, channels=[], listener=None):
        self.model_path = model_path
        self.dataset_path = dataset_path

        # redis channel
        threading.Thread.__init__(self)

        if listener is None:
            self.listener = MLListener(channels=channels)
        else:
            self.listener = listener

        self.refresh_model()

        self.model = None

    def refresh_model(self):
        if hasattr(self.model, "before_reload_model"):
            self.model.before_reload_model()

        raise NotImplementedError

    def get_model(self):
        return self.model

    def unsubscribe(self):
        self.listener.unsubscribe()

    def run(self):
        print("Run {} thread...".format(self.listener.get_channels()))

        for item in self.listener.listen():
            if item['data'] == 'KILL':
                self.unsubscribe()

                break
            elif item['data'] == 'NEW_MODEL':
                self.refresh_model()

'''
class MLModel(object):
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

        # assign the session to the attribute when the backend is 'tensorflow'
        if K._BACKEND == "tensorflow":
            self.session = tf.Session()
            K.set_session(self.session)

        # load weights into new model
        loaded_model.load_weights(self.model_path + "/model.h5")

        # warm up
        loaded_model.predict(np.array([[2,3,4,1]]))

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

    def before_reload_model(self):
        if K._BACKEND == "tensorflow" \
            and hasattr(self, "model") \
            and hasattr(self.model, "session"):

            self.model.session.close()
'''
