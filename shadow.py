#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

from exception import *
from connection import __NetLinkConn


class Profile(__NetLinkConn):
    '''
    Profile object: builds a <Profile> object from the "pid" provided on
    initialization.
    '''

    STAT_FIELDS = ['pid', 'tcomm', 'state', 'ppid', 'pgrp', 'sid', 'tty_nr', 
                   'tty_pgrp', 'flags', 'min_flt', 'cmin_flt', 'maj_flt',
                   'cmaj_flt', 'utime', 'stime', 'cutime', 'cstime',
                   'priority', 'nice', 'num_threads', 'it_real_value', 
                   'start_time', 'vsize', 'rss', 'rsslim', 'start_code', 
                   'end_code', 'start_stack', 'esp', 'eip', 'pending', 
                   'blocked', 'sigign', 'sigcatch', 'wchan', 'NONE', 'NONE', 
                   'exit_signal', 'task_cpu', 'rt_priority', 'policy', 
                   'blkio_ticks', 'gtime', 'cgtime', 'start_data', 'end_data', 
                   'arg_start', 'arg_end', 'env_start', 'env_end', 'exit_code'
                  ]

    PROC_STATES = {'R':'running', 'S':'interruptible_sleep', 
                   'D':'uninterruptible_disk_sleep', 'Z':'zombie', 
                   'T':'traced', 'W':'paging'
                  }

    def __init__(self, pid):
        super(Profile, self).__init__()
        self.pid = pid
        self.__rst_state = self.rBytes() 
        self.__wst_state = self.wBytes()
        self._last_r = self.__rst_state
        self._last_w = self.__wst_state

    @property
    def is_alive(self):
        '''
        Class property: returns <type 'bool'> response of processes state.
        '''
        all_processes = filter(lambda i: i.isdigit(), os.listdir('/proc'))
        if self.pid in map(int, all_processes):
            return True
        return False

    @property
    def ppid(self):
        '''
        Class property: returns <type 'int'> of the profiled pid's parent.
        '''
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
        '''
        Class property: returns <type 'str'> of profiled pid's name.
        '''
        try:
            with open('/proc/%s/comm' % self.pid) as f:
                pid_name = f.read()
                name = pid_name.strip('\n')
        except IOError:
            raise BadProcess(self.pid)
        return name

    @property
    def fds(self):
        '''
        Class property: returns <type 'int'> of open file-descriptors of 
        profiled pid.
        '''
        try:
            fds = os.listdir('/proc/%s/fd' % self.pid)
        except OSError:
            raise BadProcess(self.pid)
        return len(fds)

    @property
    def gid(self):
        '''
        Class property: returns <type 'str'> or <type 'NoneType'> of profiled 
        pids group id.
        '''
        attrs = self.__pid_status_attrs()
        gid = attrs.get('gid')
        if gid:
            return gid[0]

    @property
    def threads(self):
        '''
        Class property: returns <type 'str'> or <type 'NoneType'> of profiled 
        pids thread count.
        '''
        attrs = self.__pid_status_attrs()
        threads = attrs.get('threads')
        if threads:
            return threads[0]

    @property
    def state(self):
        '''
        Class property: returns <type 'str'> or <type 'NoneType'> of profiled
        pids current state.
        '''
        attrs = self.__pid_stat_attrs()
        state = attrs.get('state')
        return self.PROC_STATES[state]

    def rBytes(self):
        '''
        Class method: returns <type 'int'> of pids total read bytes since 
        startup.
        '''
        read = self._ntlnk_exchange()
        return read[0]

    def wBytes(self):
        '''
        Class method: returns <type 'int'> of the pids total write bytes since 
        startup.
        '''
        write = self._ntlnk_exchange()
        return write[1]

    def has_read(self):
        '''
        Class method: returns <type 'bool'> for pid's reads since last call.
        '''
        current_r = self.rBytes()
        if current_r > self._last_r:
            self._last_r = current_r
            return True
        return False

    def has_write(self):
        '''
        Class method: returns <type 'bool'> for the pids writes since last call.
        '''
        current_w = self.wBytes()
        if current_w > self._last_w:
            self._last_w = current_w
            return True
        return False

    def allread(self):
        '''
        Class method: returns <type 'int'> for pids total reads since object
         creation.
        '''
        current_r = self.rBytes()
        return current_r - self.__rst_state

    def allwrite(self):
        '''
        Class method: returns <type 'int'> for the pids total writes since
        object creation.
        '''
        current_w = self.wBytes()
        return current_w - self.__wst_state

    def __pid_status_attrs(self):
        '''
        Private class method: (not meant to be called directly) populates a
        <type 'dict'> with pid attributes read from "status".
        '''
        try:
            with open('/proc/%s/status' % self.pid) as f:
                raw_attrs = f.read()
        except IOError:
            raise BadProcess(self.pid)
        pid_attrs = {i[0].strip(':').lower():i[1:] for i in
                     [attr.split() for attr in raw_attrs.split('\n')] if i}
        return pid_attrs

    def __pid_stat_attrs(self):
        '''
        Private class method: (not meant to be called directly) populates a
        <type 'dict'> with pid attributes read from "stat".
        '''
        try:
            with open('/proc/%s/stat' % self.pid) as f:
                stats = f.read()
        except IOError:
            raise BadProcess(self.pid)
        pid_stats = dict(zip(self.STAT_FIELDS, stats.split()))
        return pid_stats

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s %s" % (self.__class__, self.pid)
