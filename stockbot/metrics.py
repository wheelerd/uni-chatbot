#!/usr/bin/env python3
from os.path import dirname, realpath


_METRICS_FILE = dirname(realpath(__file__)) + "/metrics/apiMetrics.txt"


def getMetrics():
    count = 0
    try:
        with open(_METRICS_FILE, "r") as fd:
            countLine = fd.readline()
            count = int(countLine.strip())
    except Exception as e:
        print("Exception while reading metrics file: ", e)
    return count

def addQueryToMetrics():
    count = getMetrics() + 1
    with open(_METRICS_FILE, "w") as fd:
        fd.write(str(count))
    return count
