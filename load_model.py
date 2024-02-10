# -*- coding: utf-8 -*-
"""Load Model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CnM4IpjNR-VDFbqUuaVm96Q0cMkzkeAu
"""

import pandas as pd
import matplotlib.pyplot as plt
import keras
import tensorflow as tf
import requests
import numpy as np
import csv

from datetime import date
from datetime import timedelta
from bs4 import BeautifulSoup

# Load the Drive helper and mount
from google.colab import drive
drive.mount('/content/drive')

#!pip freeze

"""To get the training data mean and std for the features"""

path = ""

def preprocessdata():
  with open(path + 'Preprocessing_Data.csv', newline='') as f:
      reader = csv.reader(f)
      data = list(reader)

  version = int(*data[0])
  mean = data[2]
  std = data[3]

  for i in range(len(mean)):
    mean[i] = float(mean[i])
    std[i] = float(std[i])
  return version, mean, std


def normalize(data, mean, std):
  data['Temp (F)'] = (data['Temp (F)'] - mean[0])/std[0]
  data['Humidity'] = (data['Humidity'] - mean[1])/std[1]
  data['Wind Speed (in HG)'] = (data['Wind Speed (in HG)'] - mean[2])/std[2]
  data['Wind Gust (MPH)'] = (data['Wind Gust (MPH)'] - mean[3])/std[3]
  return data


getdata(mean, std):
  pd_data = pd.read_csv(path+'weather_data.csv')
  pd_data = pd_data.iloc[-60:]
  pd_data.reset_index(drop=True, inplace=True)

  time_data = pd.DataFrame()
  time_data['Time'] = pd.to_datetime(pd_data['Time PST'])
  pd_data = pd_data.drop(['Time PST'], axis = 1)
  pd_data['Temp (F)'] = pd_data['Temp (F)'].astype(int)
  pd_data['Humidity'] =  pd_data['Humidity'].astype(int)
  pd_data['Wind Speed (in HG)'] = pd_data['Wind Speed (in HG)'].astype(float)
  pd_data['Wind Gust (MPH)'] = pd_data['Wind Gust (MPH)'].astype(float)
  df = normalize(pd_data, mean, std)
  return df


def model_predict(df, model):
  tf_data = tf.convert_to_tensor(df)
  tf_data = tf.reshape(tf_data, [1, *tf_data.shape])
  prediction = model.predict(tf_data, verbose = 0)
  df.loc[len(df.index)] = [*prediction[0]]
  df = df.iloc[-60:]
  return prediction[0][0]


def main():
  version, mean, std = preprocessdata()
  df = getdata(mean, std)
  
  today = date.today() - timedelta(days = 1)
  result = pd.DataFrame(columns=['Time PST', 'Temp (F)'])
  model = tf.keras.models.load_model(path + 'LTSM{}.h5'.format(version))
  
  for i in range(24):
    temperature = int(model_predict(df, model)*std[0] + mean[0])
    time = ""
    if i < 10:
      time = "{} 0{}:57:00 AM".format(today, i)
      #print(time + ', Temp {} (F)'.format(temperature))
    elif i < 12:
      time = "{} {}:57:00 AM".format(today, i)
      #print(time + ', Temp {} (F)'.format(temperature))
    else:
      time = "{} 0{}:57:00 PM".format(today, i)
      #print(time + ', Temp {} (F)'.format(temperature))
    result.loc[len(result.index)] = [time, temperature]

  result.to_csv(path+'model_prediction.csv', mode='a', index=False, header=False)
  remove_dup = pd.read_csv(path+'model_prediction.csv')
  remove_dup = remove_dup.drop_duplicates(subset=['Time PST'])
  remove_dup.to_csv(path+'model_prediction.csv', mode = 'w', index=False, header=True)

if __name__ == "__main__":
    main()
