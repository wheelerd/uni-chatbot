#!/usr/bin/env python3
from ..query import queryChatbot


def query(queries):
    if "query" not in queries.keys():
        raise RESTError(0, "Query parameter 'query' missing")
    
    answer = queryChatbot(queries["query"][0])
    return {"response": answer}
