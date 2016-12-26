import os

import numpy as np

from utils.env import logger
from basic.algorithm import MLAlgorithm

from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.utils import np_utils
from sklearn.model_selection import train_test_split


def encode_one_hot(arr):
    uniques, ids = np.unique(arr, return_inverse=True)

    return np_utils.to_categorical(ids, len(uniques)), uniques


class IrisDNN(MLAlgorithm):
    def split_data(self, train_size=0.5, random_state=1201):
        train_X, test_X, train_y, test_y = train_test_split(
            self.dataset.X, self.dataset.Y, train_size=train_size, random_state=random_state)

        train_y_ohe, uniques = encode_one_hot(train_y)
        test_y_ohe, _ = encode_one_hot(test_y)
        self.classes = uniques

        return train_X, train_y_ohe, test_X, test_y_ohe

    def build_network(self):
        self.model = Sequential()

        # layer 1: 4 -> 16
        self.model.add(Dense(input_dim=4, output_dim=16))
        self.model.add(Activation(('relu')))
        self.model.add(Dropout(0.2))

        # layer 2: 16 -> 16
        self.model.add(Dense(output_dim=16))
        self.model.add(Activation(('relu')))
        self.model.add(Dropout(0.2))

        # output: 16 -> 3
        self.model.add(Dense(3))
        self.model.add(Activation('softmax'))

    def train_model(self):
        # Prepare input
        train_X, train_y_ohe, test_X, test_y_ohe = self.split_data()

        # build network
        self.build_network()

        # Adam: A Method for Stochastic Optimization: https://arxiv.org/abs/1412.6980
        self.model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

        # Start fit
        self.model.fit(train_X, train_y_ohe, nb_epoch=100, batch_size=10)
        loss, accuracy = self.model.evaluate(test_X, test_y_ohe)

        logger.info("Accuracy = {:.2f}".format(accuracy))

    def save_model(self):
        # serialize model to JSON
        model_json = self.model.to_json()

        # Create folder if the targeted folder is NOT existing
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)

        with open(os.path.join(self.model_path, "iris_model.json"), "w") as json_file:
            json_file.write(model_json)

        # serialize weights to HDF5
        self.model.save_weights(os.path.join(self.model_path, "model.h5"))
        np.save(os.path.join(self.model_path, "classes"), self.classes)

        print("Saved model to disk")
