#!/usr/bin/env python3
from ..metrics import getMetrics


def getStats(queryString):
    apiCalls = getMetrics()
    return {"apiCalls": apiCalls}
