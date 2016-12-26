from basic.listener import MLListener
from event import EVENT_KILL, EVENT_NEW, EVENT_TRAIN
from utils.env import logger

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
        params = {"dataset": self.dataset(),
                  "model_path": self.model_path}

        self.model = self.class_model(params)

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
