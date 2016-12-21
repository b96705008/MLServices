import redis
import threading

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EVENT_NEW = "NEW_MODEL"
EVENT_TRAIN = "BUILD_MODEL"
EVENT_KILL = "KILL"

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

    def publish(self, channel, event):
        self.redis.publish(channel, event)

    def unsubscribe(self):
        self.pubsub.unsubscribe()
        logger.info('{} tries to unsubscribe the channelds successfully'.format(type(self).__name__))

    def subscribe(self, channels):
        self.pubsub.subscribe(channels)


class MLEngine(object):
    def __init__(self, dataset_path, model_path, channels=[], listener=None):
        self.model_path = model_path
        self.dataset_path = dataset_path

        # redis channel
        #threading.Thread.__init__(self)

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

    def run(self):
        print("Run {} thread...".format(self.listener.get_channels()))

        for item in self.listener.listen():
            if item['data'] == EVENT_KILL:
                self.listener.unsubscribe()

                break
            elif item['data'] == EVENT_NEW:
                self.refresh_model()

class MLBuilder(object):
    def __init__(self, dataset_path, model_path, channels=[], listener=None):
        self.model_path = model_path
        self.dataset_path = dataset_path

        if listener is None:
            self.listener = MLListener(channels=channels)
        else:
            self.listener = listener

    def build_model(self):
        raise NotImplementedError

    def build(self, channels, event=EVENT_TRAIN):
        self.build_model()

        # publish
        self.listener.publish(channels, event)

    def run(self):
        print("Listen build {} model command...".format(self.listener.get_channels()))

        for item in self.listener.listen():
            if item['data'] == EVENT_KILL:
                self.listener.unsubscribe()

                break
            elif item['data'] == EVENT_TRAIN:
                self.build(self.listener.get_channels())
