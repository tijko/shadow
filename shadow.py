#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

from exception import *
from connection import __NetLinkConn


class Profile(__NetLinkConn):

    def __init__(self, pid):
        super(Profile, self).__init__()
        self.pid = pid
        self.__rst_state = self.rBytes() 
        self.__wst_state = self.wBytes()
        self._last_r = self.__rst_state
        self._last_w = self.__wst_state

    @property
    def is_alive(self):
        all_processes = filter(lambda i: i.isdigit(), os.listdir('/proc'))
        if self.pid in map(int, all_processes):
            return True
        return False

    @property
    def parent(self):
        try:
            with open('/proc/%s/stat' % self.pid) as f:
                pid_stats = f.read()
        except IOError:
            raise BadProcess(self.pid)
        pid_stat_arr = pid_stats.split()
        ppid = int(pid_stat_arr[3])
        return ppid

    @property
    def name(self):
        try:
            with open('/proc/%s/comm' % self.pid) as f:
                pid_name = f.read()
                name = pid_name.strip('\n')
        except IOError:
            raise BadProcess(self.pid)
        return name

    @property
    def fds(self):
        try:
            fds = os.listdir('/proc/%s/fd' % self.pid)
        except OSError:
            raise BadProcess(self.pid)
        return len(fds)

    @property
    def gid(self):
        attrs = self.__pid_attrs()
        return attrs.get('gids')

    @property
    def threads(self):
        attrs = self.__pid_attrs()
        return attrs.get('threads')

    def rBytes(self):
        read = self._ntlnk_exchange()
        return read[0]

    def wBytes(self):
        write = self._ntlnk_exchange()
        return write[1]

    def has_read(self):
        current_r = self.rBytes()
        if current_r > self._last_r:
            self._last_r = current_r
            return True
        return False

    def has_write(self):
        current_w = self.wBytes()
        if current_w > self._last_w:
            self._last_w = current_w
            return True
        return False

    def allread(self):
        current_r = self.rBytes()
        return current_r - self.__rst_state

    def allwrite(self):
        current_w = self.wBytes()
        return current_w - self.__wst_state

    def __pid_attrs(self):
        try:
            with open('/proc/%s/status' % self.pid) as f:
                raw_attrs = f.readlines()
        except IOError:
            raise BadProcess(self.pid)
        attrs_lns = [i.split('\t')[:2] for i in raw_attrs]   
        attrs_parse = [(i.strip(':'), v.strip('\n')) for i,v in attrs_lns]
        pid_attrs = {k.lower():v for k,v in attrs_parse}
        return pid_attrs

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s %s" % (self.__class__, self.pid)
