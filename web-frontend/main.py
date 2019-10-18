#!/usr/bin/env python3
from http.server import ThreadingHTTPServer
from httpHandler import HTTPApiHandler

def startServer(port):
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
