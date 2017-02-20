import redis

from utils.env import logger


class MLModel(object):
    def __init__(self, params):
        self.init(params)

    def load(self):
        self.before_load_model()
        self.load_model()
        self.after_load_model()

    def before_load_model(self):
        pass

    def after_load_model(self):
        pass

    def init(self, params={}):
        for k, v in params.items():
            setattr(self, k, v)

        self.load()

    def load_model(self):
        raise NotImplementedError

    def before_reload_model(self):
        pass

    def after_reload_model(self):
        pass
