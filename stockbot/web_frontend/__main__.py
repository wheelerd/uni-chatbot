#!/usr/bin/env python3
from http.server import ThreadingHTTPServer
from os.path import dirname, realpath
from .httpHandler import HTTPApiHandler
from .fileCacher import cacheFile
from ..query import QueryHandler

def startServer(port):
    HTTPApiHandler.queryHandler = QueryHandler()
    filesPath = dirname(realpath(__file__)) + "/files"
    cacheFile(None, filesPath + "/404.html", "text/html")
    cacheFile("/404_styles.css", filesPath + "/404_styles.css", "text/css")
    cacheFile("/404.png", filesPath + "/404.png", "image/png")
    cacheFile("/index.html", filesPath + "/index.html", "text/html")
    cacheFile("/rest-caller.js", filesPath + "/rest-caller.js", "text/javascript")
    cacheFile("/styles.css", filesPath + "/styles.css", "text/css")
    cacheFile("/roboto.css", filesPath + "/roboto.css", "text/css")
    cacheFile("/Roboto-Regular.ttf", filesPath + "/Roboto-Regular.ttf", "application/octet-stream")
    cacheFile("/Roboto-Medium.ttf", filesPath + "/Roboto-Medium.ttf", "application/octet-stream")
    httpd = ThreadingHTTPServer(('', port), HTTPApiHandler)
    try:
        print("Server started")
        httpd.serve_forever()
    except Exception as e:
        print("\nException occurred, stopping: {}".format(e))
    except KeyboardInterrupt:
        print("\nGracefully stopping server...")
    httpd.server_close()
    print("Server stopped")


if __name__ == "__main__":
    startServer(8080)

