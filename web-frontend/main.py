#!/usr/bin/env python3
from http.server import ThreadingHTTPServer
from httpHandler import HTTPApiHandler
from fileCacher import cacheFile

def startServer(port):
    cacheFile("/index.html", "files/index.html", "text/html")
    cacheFile(None, "files/404.html", "text/html")
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
