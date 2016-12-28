import redis

from threading import Thread
from utils.env import logger

from event import EVENT_TRAIN, EVENT_KILL, EVENT_NEW
from listener import MLListener


class MLEngine(Thread):
    def __init__(self, dataset_path, class_model, model_path, channel, listener=None):
        Thread.__init__(self)

        self.class_model = class_model

        self.model_path = model_path
        self.dataset_path = dataset_path

        if listener is None:
            self.listener = MLListener(channel)
        else:
            self.listener = listener

        self.model = None

        self.process(skip_before=True, skip_after=True)

    def process(self, skip_before=False, skip_after=False):
        if not skip_before:
            self.before_refresh_model()

        self.refresh_model()

        if not skip_after:
            self.after_refresh_model()

    def before_refresh_model(self):
        self.model.before_reload_model()

    def refresh_model(self):
        raise NotImplementedError

    def after_refresh_model(self):
        self.model.after_reload_model()

    def get_model(self):
        return self.model

    def run(self):
        logger.info("Listen {} channel...".format(self.listener.get_channel()))

        for item in self.listener.listen():
            if item['data'] == EVENT_KILL:
                self.listener.unsubscribe()

                break
            elif item['data'] == EVENT_NEW:
                self.process()
