#!/usr/bin/env python3


def query(queries):
    if "query" not in queries.keys():
        raise RESTError(0, "Query parameter 'query' missing")
    
    return {"response": "Placeholder response (you asked: {})".format(queries["query"][0])} # TODO implement
