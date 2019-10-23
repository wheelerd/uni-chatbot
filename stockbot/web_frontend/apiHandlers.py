#!/usr/bin/env python3
from .getStatsHandler import getStats
from .queryHandler import query


apiHandlers = {
    'getStats': getStats,
    'query': query
}
