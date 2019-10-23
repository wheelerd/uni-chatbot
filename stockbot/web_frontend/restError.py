#!/usr/bin/env python3


class RESTError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
