import redis
import tensorflow as tf

from keras import backend as K

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EVENT_NEW = "NEW_MODEL"
EVENT_TRAIN = "BUILD_MODEL"
EVENT_KILL = "KILL"

class MLListener(object):
    def __init__(self, channel, r=None):
        self.channel = channel

        if r is None:
            self.redis = redis.Redis()
        else:
            self.redis = r

        self.pubsub = self.redis.pubsub()
        self.subscribe(self.channel)

    def get_channel(self):
        return self.channel

    def listen(self):
        for item in self.pubsub.listen():
            yield item

    def publish(self, channel, event):
        self.redis.publish(channel, event)

    def unsubscribe(self):
        self.pubsub.unsubscribe()
        logger.info('{} tries to unsubscribe the channelds successfully'.format(type(self).__name__))

    def subscribe(self, channel):
        self.pubsub.subscribe(channel)

class MLBuilder(object):
    def __init__(self, class_dataset, dataset_path, class_model, model_path, channels=[[], []], listener=None):
        self.class_model = class_model
        self.model_path = model_path

        self.class_dataset = class_dataset
        self.dataset_path = dataset_path

        logger.info("Apply model_class is {}, dataset_class is {}".format(self.class_model, self.class_dataset))

        self.model = None

        self.channels = channels
        if listener is None:
            self.listener = MLListener(self.channels[0])
        else:
            self.listener = listener

    def dataset(self):
        return self.class_dataset(self.dataset_path)

    def build_model(self):
        self.model = self.class_model(self.dataset(), self.model_path)
        self.model.train_model()
        self.model.save_model()

    def build(self):
        self.before_build_model()
        self.build_model()
        self.after_build_model()

    def before_build_model(self):
        pass

    def after_build_model(self, event=EVENT_NEW):
        self.listener.publish(self.channels[1], event)

    def run(self):
        print("Listen build {} model command...".format(self.listener.get_channel()))

        for item in self.listener.listen():
            if item['data'] == EVENT_KILL:
                self.listener.unsubscribe()

                break
            elif item['data'] == EVENT_TRAIN:
                self.build()

class MLDataset(object):
    def __init__(self, dataset_path):
        print('Read iris dataset...')
        self.dataset_path = dataset_path

        self.X = None
        self.Y = None

        self.prepare_data()
        self.feature_engineer()

    def prepare_data(self):
        raise NotImplementedError

    def feature_engineer(self):
        pass

class MLEngine(object):
    def __init__(self, dataset_path, class_model, model_path, channel, listener=None):
        self.class_model = class_model

        self.model_path = model_path
        self.dataset_path = dataset_path

        if listener is None:
            self.listener = MLListener(channel)
        else:
            self.listener = listener

        self.model = None
        self.process()

    def process(self):
        if hasattr(self.model, "before_reload_model"):
            self.model.before_reload_model()

        self.refresh_model()

    def refresh_model(self):
        raise NotImplementedError

    def get_model(self):
        return self.model

    def run(self):
        print("Listen {} channel...".format(self.listener.get_channel()))

        for item in self.listener.listen():
            if item['data'] == EVENT_KILL:
                self.listener.unsubscribe()

                break
            elif item['data'] == EVENT_NEW:
                self.process()

class MLModel(object):
    def __init__(self, model_path):
        self.model_path = model_path

        self.load()

    def load(self):
        # assign the session to the attribute when the backend is 'tensorflow'
        if K._BACKEND == "tensorflow":
            self.session = tf.Session()
            K.set_session(self.session)

        self.load_model()

    def load_model(self):
        raise NotImplementedError

    def predict_probs(self, features):
        raise NotImplementedError

    def predict_class(self, features):
        raise NotImplementedError

    def before_reload_model(self):
        if K._BACKEND == "tensorflow" \
            and hasattr(self, "model") \
            and hasattr(self.model, "session"):

            self.model.session.close()
