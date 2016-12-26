import redis
import tensorflow as tf
from keras import backend as K

from utils.env import logger


class MLModel(object):
    def __init__(self, params):
        self.init(params)

    def load(self):
        # assign the session to the attribute when the backend is 'tensorflow'
        if K._BACKEND == "tensorflow":
            self.session = tf.Session()
            K.set_session(self.session)

            logger.info("use the tensorflow to be the backend, we should set session firstly")

        self.load_model()

    def init(self, params={}):
        for k, v in params.items():
            setattr(self, k, v)

        self.load()

    def load_model(self):
        raise NotImplementedError

    def before_reload_model(self):
        if K._BACKEND == "tensorflow" \
            and hasattr(self, "model") \
            and hasattr(self.model, "session"):

            logger.info("due to the tensorflow, before reloading model, we should close the session firstly")

            self.model.session.close()
        else:
            pass
