#!/usr/bin/env python3
from http.server import ThreadingHTTPServer
from httpHandler import HTTPApiHandler
from fileCacher import cacheFile

def startServer(port):
    cacheFile(None, "files/404.html", "text/html")
    cacheFile("/404_styles.css", "files/404_styles.css", "text/css")
    cacheFile("/404.png", "files/404.png", "image/png")
    cacheFile("/index.html", "files/index.html", "text/html")
    cacheFile("/rest-caller.js", "files/rest-caller.js", "text/javascript")
    cacheFile("/styles.css", "files/styles.css", "text/css")
    cacheFile("/roboto.css", "files/roboto.css", "text/css")
    cacheFile("/Roboto-Regular.ttf", "files/Roboto-Regular.ttf", "application/octet-stream")
    cacheFile("/Roboto-Medium.ttf", "files/Roboto-Medium.ttf", "application/octet-stream")
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
