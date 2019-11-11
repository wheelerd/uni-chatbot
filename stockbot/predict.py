#!/usr/bin/env python3
from .alphavantage import time_series_weekly
from keras.models import model_from_json
from os.path import dirname, realpath


def load_predict_model():
    json_file = open(dirname(realpath(__file__)) + '/model/model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model=model_from_json(loaded_model_json)
    loaded_model.load_weights(dirname(realpath(__file__)) + '/model/model.h5')
    return loaded_model


def predict(loaded_model, symbol):
    t=time_series_weekly(symbol)
    inTimeseries = []
    for timestamp, data in t.items():
        clos=float(data['4. close'])
        inTimeseries.insert(0, clos)
    return loaded_model.predict(np.atleast_3d(inTimeseries))
