#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import re
from apiHandlers import apiHandlers
from restError import RESTError
from fileCacher import *


apiPathRegex = re.compile('^/api/([^/]*)$')


class HTTPApiHandler(BaseHTTPRequestHandler):
    def _serveFile(self, path):
        if path == '/':
            path = '/index.html'
        
        self.log_message('Serving file "{}"'.format(path))
        if isFileInCache(path):
            thisFile = getFileFromCache(path)
            self.send_response(200)
            self.send_header("Content-Type", thisFile.mimetype)
            self.end_headers()
            self.wfile.write(thisFile.bytebuf)
        else:
            notFoundFile = getFileFromCache(None)
            self.log_message("File missing. Sending 404 page...")
            self.send_response(404)
            self.send_header("Content-Type", notFoundFile.mimetype)
            self.end_headers()
            self.wfile.write(notFoundFile.bytebuf)

    def do_GET(self):
        try:
            # Normalise the path and extract query parameters
            processed = urlparse(self.path)
            normalPath = processed.path
            queries = parse_qs(processed.query)
            
            # Serve the request
            apiMatch = re.match(apiPathRegex, normalPath)
            if apiMatch != None:
                # Doing a REST API call
                callName = apiMatch.group(1)
                if callName in apiHandlers.keys():
                    self.log_message('Serving REST API call "{}"'.format(callName))
                    try:
                        result = apiHandlers[callName](queries)
                    except RESTError as e:
                        self.send_response(403, "REST API call failed")
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        
                        errorDict = {
                            'code': e.code,
                            'message': e.message
                        }
                        
                        json.dump(errorDict, self.wfile)
                    else:
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(result).encode("utf-8"))
                else:
                    responseMessage = 'Unknown REST API call "{}"'.format(callName)
                    self.log_message(responseMessage)
                    self.send_response(404, responseMessage)
                    self.end_headers()
            else:
                # Serving a file
                self._serveFile(normalPath)
        except:
            self.send_response_only(500)
            raise
