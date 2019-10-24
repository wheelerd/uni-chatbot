#!/usr/bin/env python3
from .metrics import addQueryToMetrics

def queryChatbot(statement):
    addQueryToMetrics()
    return statement # TODO implement, for now it just pings back the statement 
