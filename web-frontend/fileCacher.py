#!/usr/bin/env python3
import os


_fileCache = dict()


class ServerFile:
    def __init__(self, mimetype, bytebuf):
        self.mimetype = mimetype
        self.bytebuf = bytebuf


def isFileInCache(key):
    return key in _fileCache.keys()


def getFileFromCache(key):
    return _fileCache[key]


def cacheFile(key, path, mimetype):
    print("Caching file '{}' as '{}' with mimetype '{}'...".format(path, key, mimetype))
    if not os.path.isfile(path):
        raise ValueError("File '{}' does not exist!".format(path))
    
    filebuf = bytearray()
    with open(path, "rb") as fd:
        while True:
            buf = fd.read()
            if len(buf) == 0:
                break
            filebuf += bytearray(buf)
    
    _fileCache[key] = ServerFile(mimetype, bytes(filebuf))
