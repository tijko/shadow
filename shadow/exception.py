#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


'''
Exceptions for Profile objects.
'''


class BadProcess(Exception):
    '''
    Error finding pid supplied.
    '''    
    def __init__(self, pid):
        self.pid = pid

    def __str__(self):
        msg = "No process <%s>" % self.pid
        return msg


class EmptyNtlnkMsg(Exception):
    '''
    Netlink message returned an empty response.
    '''
    def __init__(self, func, pid):
        self.func = func
        self.pid = pid

    def __str__(self):
        msg = "Process <%s> returned an empty netlink response" % self.pid
        return msg


class StructParseError(Exception):
    '''
    Error parsing netlink struct.
    '''
    def __init__(self, func, pid):
        self.func = func
        self.pid = pid

    def __str__(self):
        msg = "<%s> netlink struct" % self.pid
        return msg


class NetlinkError(Exception):
    '''
    Message returned an netlink error response.
    '''
    def __init__(self, errno, pid):
        self.pid = pid
        self.err = os.strerror(-errno)

    def __str__(self):
        msg = "%s <%s>" % (self.err, self.pid)
        return msg

class InsufficientRights(Exception):
    '''
    Error on user access to netlink.
    '''
    def __init__(self, func, pid):
        self.func = func
        self.pid = pid

    def __str__(self):
        msg = "Process <%s> is running under user id" % self.pid
        return msg

class InvalidPath(Exception):
    '''
    Error returned on an invalid path supplied for a file read.
    '''
    def __init__(self, fpath):
        self.fpath = fpath

    def __str__(self):
        msg = "Invalid path <%s>" % self.fpath
        return msg
