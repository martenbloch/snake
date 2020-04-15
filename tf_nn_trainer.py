import tensorflow as tf
from tensorflow import keras
import sys
import numpy as np

import training_data as td
from common import Dir

if __name__ == "__main__":

    print(tf.__version__)

    n_args = len(sys.argv)
    model_name = sys.argv[1]
    files = []
    for i in range(2, n_args):
        files.append(sys.argv[i])

    model = keras.Sequential([
        keras.layers.Flatten(input_shape=(1, 5)),
        keras.layers.Dense(174, activation=tf.nn.relu6),
        keras.layers.Dense(4, activation=tf.nn.softmax)
    ])

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    train_in, train_out = td.import_training_data(*files)

    model.fit(train_in, train_out, epochs=50)

    #evaluation
    test_in = np.ndarray(shape=(1, 1, 5))
    train_in[0] = [False, False, False, True, 0]

    test_out = np.argmax(model.predict(test_in))
    print("test out:{}".format(test_out))

    tf.keras.models.save_model(model, model_name, overwrite=True, include_optimizer=True)

