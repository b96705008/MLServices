from basic.interface import MLEngine

class IrisEngine(MLEngine):
    def refresh_model(self):
        print("refresh iris model... ")

        self.model = self.class_model(self.model_path)
