#!/usr/bin/env python
# -*- coding: utf-8 -*-


class BadProcess(Exception):
    
    def __init__(self, pid):
        self.pid = pid

    def __str__(self):
        msg = "No process <%s>" % self.pid
        return msg


class EmptyNtlnkMsg(Exception):

    def __init__(self, func, pid):
        self.func = func
        self.pid = pid

    def __str__(self):
        msg = "Process <%s> returned an empty netlink response" % self.pid
        return msg


class StructParseError(Exception):

    def __init__(self, func, pid):
        self.func = func
        self.pid = pid

    def __str__(self):
        msg = "Error parsing process <%s> netlink struct" % self.pid
        return msg
