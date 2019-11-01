#!/usr/bin/env python3
from io import BytesIO
from base64 import b64encode
from ..query import queryChatbot


def query(queries):
    if "query" not in queries.keys():
        raise RESTError(0, "Query parameter 'query' missing")
    
    answer, image = queryChatbot(queries["query"][0])
    
    # Encode image as base64
    if image == None:
        imageBase64 = None
    else:
        byteBuffer = BytesIO()
        image.save(byteBuffer, format='PNG')
        imageBase64 = b64encode(byteBuffer.getvalue()).decode("utf-8")

    return {"response": answer, "image": imageBase64}
