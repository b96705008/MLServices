class MLAlgorithm(object):
    def __init__(self, params):
        self.init(params)

        self.process()

    def process(self):
        self.train_model()
        self.save_model()

    def init(self, params):
        for k, v in params.items():
            setattr(self, k, v)

    def train_model(self):
        raise NotImplementedError

    def save_model(self):
        raise NotImplementedError
