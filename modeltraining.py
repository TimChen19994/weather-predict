# -*- coding: utf-8 -*-
"""ModelTraining.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1g8XfXJQFrvtAxDsWj9EQ5ZT90A-C-T-7
"""
import pandas as pd
import matplotlib.pyplot as plt
import keras
import requests
import pandas as pd
import numpy as np
from datetime import date
from datetime import timedelta
from bs4 import BeautifulSoup
import csv


path = ''

def preprocesshyper():
    with open(path + 'data/' + 'preprocessing_data.csv', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)

    version = int(*data[0])
    version += 1

    with open(path + 'data/' + "preprocessing_data.csv", "w") as f:
        f.write("{}\n".format(version))
    return version

def normalize(data):
    data_mean = data.mean(axis=0)
    data_std = data.std(axis=0)
    with open(path + 'data/ + "preprocessing_data.csv", "a") as f:
        f.write("Mean, Standard Deviation\n")
        f.write("{}, {}, {}, {}\n".format(data_mean[0], data_mean[1], data_mean[2], data_mean[3]))
        f.write("{}, {}, {}, {}".format(data_std[0], data_std[1], data_std[2], data_std[3]))
    return (data - data_mean) / data_std


def preprocessdata():
    pd_data = pd.read_csv(path + 'data/ + 'weather_data.csv')
    pd_data['Time PST'] = pd.to_datetime(pd_data['Time PST'])
    pd_data['Temp (F)'] = pd_data['Temp (F)'].astype(int)
    pd_data['Humidity'] = pd_data['Humidity'].astype(int)
    pd_data['Wind Speed (in HG)'] = pd_data['Wind Speed (in HG)'].astype(float)
    pd_data['Wind Gust (MPH)'] = pd_data['Wind Gust (MPH)'].astype(float)

    pd_data = pd_data.drop(['Time PST'], axis=1)
    df = normalize(pd_data)

    return df


def model_train(df):
    """This is to split the data set into training and validation set"""

    split_fraction = 0.715
    train_split = int(split_fraction * int(df.shape[0]))
    step = 1

    past = 60  # Sequence length
    future = 0  # Amount of sequence in the future to predict
    learning_rate = 0.001
    batch_size = 1  # how many predictions per sample
    epochs = 20

    train_data = df.loc[0: train_split - 1]
    val_data = df.loc[train_split:]

    """
    The starting point for y_train must be at start as we take that (past) input to predict another output
    
    for example using three sequence (past= 3):
      data = [0,1,2,3,4,5,6,7,8,9,10]
      split
      x_train = [0,1,2,3,4]
      y_train = [3,4,5]
    
      [0,1,2] -> [3]
      [1,2,3] -> [4]
      [2,3,4] -> [5]
    
    The step is to sample at every integer steps. (1,2,3,4), (1,3,5,7), ...
    """

    start = past + future
    end = start + train_split

    x_train = train_data.values
    y_train = df.iloc[start:end]

    sequence_length = int(past / step)

    dataset_train = keras.preprocessing.timeseries_dataset_from_array(
        x_train,
        y_train,
        sequence_length=sequence_length,
        sampling_rate=step,
        batch_size=batch_size,
    )

    """
    
    The x_end must be subtracted by 1
    
    for example using three sequence (past = 3):
      data = [0,1,2,3,4,5,6,7,8,9,10]
      split
      x_val = [5,6,7,8,9,10]
      y_val = [8,9,10]
    
      [5,6,7] -> [8]
      [6,7,8] -> [9]
      [7,8,9] -> [10]
    
      [8,9,10] -> [?]  # is unknown
    
    """

    x_end = len(val_data) - 1

    label_start = train_split + past + future

    x_val = val_data.iloc[:x_end].values
    y_val = df.iloc[label_start:]

    dataset_val = keras.preprocessing.timeseries_dataset_from_array(
        x_val,
        y_val,
        sequence_length=sequence_length,
        sampling_rate=step,
        batch_size=batch_size,
    )

    for batch in dataset_train.take(1):
        inputs, targets = batch

    """
    
    (1, 60, 5)
    1 is batch size
    60 is sequence length
    5 is features

    """

    inputs = keras.layers.Input(shape=(inputs.shape[1], inputs.shape[2]))
    lstm_out = keras.layers.LSTM(32)(inputs)
    outputs = keras.layers.Dense(4)(lstm_out)

    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=learning_rate), loss="mse")
    model.summary()

    es_callback = keras.callbacks.EarlyStopping(monitor="val_loss", min_delta=0, patience=5)

    modelckpt_callback = keras.callbacks.ModelCheckpoint(
        monitor="val_loss",
        verbose=1,
        save_weights_only=True,
        save_best_only=True,
    )

    history = model.fit(
        dataset_train,
        epochs=epochs,
        validation_data=dataset_val,
        callbacks=[es_callback, modelckpt_callback],
    )
    return model

    
    # def visualize_loss(history, title):
    #     loss = history.history["loss"]
    #     val_loss = history.history["val_loss"]
    #     epochs = range(len(loss))
    #     plt.figure()
    #     plt.plot(epochs, loss, "b", label="Training loss")
    #     plt.plot(epochs, val_loss, "r", label="Validation loss")
    #     plt.title(title)
    #     plt.xlabel("Epochs")
    #     plt.ylabel("Loss")
    #     plt.legend()
    #     plt.show()
    #
    #
    # visualize_loss(history, "Training and Validation Loss")
    #
    # def show_plot(plot_data, delta, title):
    #     labels = ["History", "True Future", "Model Prediction"]
    #     marker = [".-", "rx", "go"]
    #     time_steps = list(range(-(plot_data[0].shape[0]), 0))
    #     if delta:
    #         future = delta
    #     else:
    #         future = 0
    #
    #     plt.title(title)
    #     for i, val in enumerate(plot_data):
    #         if i:
    #           if i == 2:
    #             plt.plot(future, plot_data[i][0], marker[i], markersize=10, label=labels[i])
    #           else:
    #             plt.plot(future, plot_data[i][0], marker[i], markersize=10, label=labels[i])
    #         else:
    #             plt.plot(time_steps, plot_data[i].flatten(), marker[i], label=labels[i])
    #     plt.legend()
    #     plt.xlim([time_steps[0], (future + 5) * 2])
    #     plt.xlabel("Time-Step")
    #     plt.show()
    #     return
    #
    #
    # for x, y in dataset_val.take(5):
    #     print(x.shape)
    #     print(model.predict(x))
    #     show_plot(
    #         [x[0][:, 1].numpy(), y[0].numpy(), model.predict(x)[0]],
    #         12,
    #         "Single Step Prediction",
    #     )
def main():
    version = preprocesshyper()
    df = preprocessdata()
    model = model_train(df)
    model.save(path + 'model/ + 'LTSM{}.h5'.format(version))

if __name__ == "__main__":
    main()
