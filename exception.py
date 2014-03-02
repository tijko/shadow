#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        msg = "Error parsing process <%s> netlink struct" % self.pid
        return msg

class NetlinkError(Exception):
    '''
    Message returned an netlink error response.
    '''
    def __init__(self, pid):
        self.pid = pid

    def __str__(self):
        msg = "Error message returned from netlink <%s>" % self.pid
        return msg
