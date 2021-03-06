#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

from functools import partial
from collections import namedtuple

from libshadow import *
from exception import *
from taskstats.taskstats import Taskstats
from priorities import nice, setnice, ioprio


class Profile(object):
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
        self.pid = pid
        self.__taskstats = Taskstats(self.pid)
        self.__rst_state = self.rBytes()
        self.__wst_state = self.wBytes()
        self._last_r = self.__rst_state
        self._last_w = self.__wst_state
        self.__st_switches = self.__pid_status_attrs.get(
                                 'voluntary_ctxt_switches')
        if self.__st_switches is None:
            self.__st_switches = 0
        
    @property
    def is_alive(self):
        '''
        Class property.getter: returns <type 'bool'> response of processes 
        state.
        '''
        all_processes = filter(lambda i: i.isdigit(), os.listdir('/proc'))
        return self.pid in map(int, all_processes)

    @is_alive.setter
    def is_alive(self, state):
        '''
        Class property.setter: returns <type 'NoneType'> sets the is_alive 
        property to False if ending the process is needed.
        '''
        if not isinstance(state, bool):
            raise TypeError
        if not self.tgid:
            raise BadProcess(self.pid)
        tkill(self.tgid, self.pid, SIGKILL)
        
    @property
    def ppid(self):
        '''
        Class property: returns <type 'int'> of the profiled pid's parent.
        '''
        pid_stats = self.file_reader('/proc/%s/stat' % self.pid)
        return int(pid_stats.split()[3])

    @property
    def name(self):
        '''
        Class property: returns <type 'str'> of profiled pid's name.
        '''
        pid_name = self.file_reader('/proc/%s/comm' % self.pid)
        return pid_name.strip('\n')

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
        gid = self.__pid_status_attrs.get('gid')
        if gid:
            return gid[0]
        return

    @property
    def tgid(self):
        '''
        Class property: returns <type 'int'> of profiled pids thread group id.
        '''
        tgid = self.__pid_status_attrs.get('tgid')
        if tgid:
            return int(tgid[0])
        return 

    def get_tids(self):
        '''
        Class method: returns <type 'list'> of profiled pids thread ids.
        '''
        threads_path = '/proc/%d/task/' % self.pid
        threads = os.listdir(threads_path)
        return threads

    @property
    def threads(self):
        '''
        Class property: returns <type 'int'> or <type 'NoneType'> of profiled 
        pids thread count.
        '''
        threads = self.__pid_status_attrs.get('threads')
        if threads:
            return int(threads[0])
        return

    @property
    def state(self):
        '''
        Class property: returns <type 'str'> or <type 'NoneType'> of profiled
        pids current state.
        '''
        state = self.__pid_stat_attrs.get('state')
        if state:
            return self.PROC_STATES[state]
        return 'Unknown'

    def load_aux_attrs(self):
        '''
        Class method: returns <type 'NoneType'>, this method creates additional
        auxillary instance attributes.
        '''
        aux_attrs = self.__pid_status_attrs
        for attr in aux_attrs:
            if not aux_attrs[attr]: continue
            attr_value = ' '.join(aux_attrs[attr])
            if not hasattr(self, attr):
                setattr(self, 'aux_' + attr, attr_value)            

    def update_aux_attrs(self):
        '''
        Class method: returns <type 'NoneType'>, this method updates the
        auxillary attributes (if load_aux_attrs methods has already been)
        called.
        '''
        aux_attrs = self.__pid_status_attrs
        for attr in aux_attrs:
            if hasattr(self, 'aux_' + attr):
                aux_attr = 'self.aux_' + attr
                update_value = ' '.join(aux_attrs[attr])
                exec("%s = '%s'" % (aux_attr, update_value))
     
    def nice(self):
        '''
        Class method: returns <type 'int'> of profiled pids niceness.
        '''
        return nice(self.pid)

    def setnice(self, level):
        '''
        Class method: sets the niceness of profiled pid, returns
        <type 'NoneType'>.

        @type 'level': <type 'int'>
        @param 'level': the new nice to set profiled pid to.
        '''
        setnice(self.pid, level)
        return 

    def ioprio(self):
        '''
        Class method: returns <type 'tuple'> of profiled pids IO_Priority
        class and ioprio_nice. 
        '''
        return ioprio(self.pid)
        
    def switches(self):
        '''
        Class method: returns <type 'int'> for the number of context switches
        of profiled pid.
        '''
        switches = self.__pid_status_attrs.get('voluntary_ctxt_switches')
        if switches:
            return int(switches[0])
        return

    def has_switched(self):
        '''
        Class method: returns <type 'bool'> to signal if there have voluntary
        context switches since initialization or last call of this method.
        '''
        current_switches = self.__pid_status_attrs.get(
                                'voluntary_ctxt_switches')
        if current_switches > self.__st_switches:
            self.__st_switches = current_switches
            return True
        return False

    def rBytes(self):
        '''
        Class method: returns <type 'int'> of pids total read bytes since 
        startup.
        '''
        try:
            bytes_read = self.__taskstats.read()
        except InsufficientRights:
            bytes_read = self.procfs_read()
        return bytes_read

    def wBytes(self):
        '''
        Class method: returns <type 'int'> of the pids total write bytes since 
        startup.
        '''
        try:
            bytes_written = self.__taskstats.write()
        except InsufficientRights:
            bytes_written = self.procfs_write()
        return bytes_written

    def procfs_read(self):
        read = self.file_reader('/proc/%s/io' % self.pid)
        return int(read.split()[1])
 
    def procfs_write(self):
        write = self.file_reader('/proc/%s/io' % self.pid)
        return int(write.split()[3])
 
    def has_read(self):
        '''
        Class method: returns <type 'bool'> for pid's reads since 
        initialization or the last call of this method.
        '''
        current_r = self.rBytes()
        if current_r > self._last_r:
            self._last_r = current_r
            return True
        return False

    def has_write(self):
        '''
        Class method: returns <type 'bool'> for the pids writes since 
        initialization or last call of this method.
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

    def smap(self):        
        '''
        Class method: returns <type 'dict'> of namedtuples for the profiled
        pids mapping memory consumption.
        '''
        smap_tuple = namedtuple('smap', ['Size', 'Rss', 'Pss', 'Shared_Clean', 
                                         'Shared_Dirty', 'Private_Clean', 
                                         'Private_Dirty', 'Referenced', 
                                         'Anonymous', 'AnonHugePages', 'Swap', 
                                         'KernelPageSize', 'MMUPageSize',
                                         'Locked', 'VmFlags']
                               )
        proc_smap = self.file_reader('/proc/%s/smaps' % self.pid).split('\n')
        proc_smaps = [proc_smap[i:i + 16] for i in 
                      xrange(0, len(proc_smap), 16)]
        smappings = dict()
        rm_newline = lambda ln: ln.strip('\n')
        for smap in proc_smaps:
            if not smap[0]: continue
            path_name = smap[0].split()[-1]
            _smap = [''.join(i.split()[1:]) for i in smap[1:]]
            _smap = map(rm_newline, _smap)
            smappings[path_name] = smap_tuple(*_smap)
        return smappings

    def pmap(self):
        '''
        Class method: returns <type 'tuple'> of the profiled pids memory map.
        '''
        return tuple(self.smap().keys())

    def wchan(self):
        '''
        Class method: returns <type 'str'> of a kernel symbol where the profiled 
        pid currently sleeping(if at all).
        '''
        wchan = self.file_reader('/proc/%s/wchan' % self.pid)
        return wchan

    def fdstat(self):
        '''
        Class method: returns <type 'dict'> for all file-descriptors as the keys
        and tuple for the files stats.
        '''
        path = '/proc/%s/fd/' % self.pid
        path_constructor = partial(lambda drt, fn: os.path.join(drt, fn), path)
        try:
            fds = map(path_constructor, os.listdir(path))
            fdstat = dict(zip(map(os.readlink, fds), map(os.stat, fds)))
        except IOError:
            raise BadProcess(self.pid)
        return fdstat

    def fdperms(self):
        '''
        Class method: returns <type 'dict'> for all file-descriptors real path
        as keys and their file permissions as octal values.
        '''
        fdstats = self.fdstat()
        permission_mask = lambda mask: oct(mask & 0777)
        modes = [fdstats[i].st_mode for i in fdstats]
        permissions = dict(zip(fdstats.keys(), map(permission_mask, modes)))
        return permissions

    def curlimit(self, resource):
        '''
        Class method: returns <type 'int'> for the current soft-limit of
        process.
        '''
        return curlimit(self.pid, resource)

    def maxlimit(self, resource):
        '''
        Class method: returns <type 'int'> for the current hard-limit of
        process.
        '''
        return maxlimit(self.pid, resource)

    def iso(self):
        '''
        Class method: returns <type 'NoneType'> :: sets the profiled process
        to run on one core and all others run on other cores.
        '''
        iso(self.pid)
        return

    def release_iso(self):
        '''
        Class method: returns <type 'NoneType'> :: releases a process that has
        been isolated.
        '''
        release_iso(self.pid)
        return

    def affinity(self):
        '''
        Class method: returns <type 'int'> for the number of cpus currently in
        processes cpu set.
        '''
        return affinity(self.pid)

    def start_time(self):
        '''
        Class method: returns <type 'float'> of seconds since boot that the 
        process started at.
        '''
        sc_clk_tck = os.sysconf('SC_CLK_TCK')
        uptime_data = self.file_reader('/proc/uptime')
        stat_data = self.file_reader('/proc/%s/stat' % self.pid)
        uptime = float(uptime_data.split()[0])
        start_time = float(stat_data.split()[21])
        return uptime - (start_time / sc_clk_tck)

    def file_reader(self, fpath):
        '''
        Class method: returns <type 'str'> for the file contents of fpath.
        '''
        try:
            with open(fpath) as f:
                raw_file_data = f.read()
        except IOError:
            raise InvalidPath(fpath)
        return raw_file_data

    @property
    def __pid_status_attrs(self):
        '''
        Private class property: (not meant to be called directly) populates a
        <type 'dict'> with pid attributes read from "status".
        '''
        raw_attrs = self.file_reader('/proc/%s/status' % self.pid)
        pid_attrs = {i[0].strip(':').lower():i[1:] for i in 
                     map(str.split, raw_attrs.split('\n')) if i}
        return pid_attrs

    @property
    def __pid_stat_attrs(self):
        '''
        Private class property: (not meant to be called directly) populates a
        <type 'dict'> with pid attributes read from "stat".
        '''
        stats = self.file_reader('/proc/%s/stat' % self.pid)
        pid_stats = dict(zip(self.STAT_FIELDS, stats.split()))
        return pid_stats

    def tgkill(self, tid, sig):
        '''
        Class method: returns <type 'NoneType'> :: sends signal 'sig' to thread
        'tid' in thread group 'tgid'.
        '''
        tgid = self.tgid
        if not tgid:
            raise BadProcess(self.pid)
        else:
            tkill(tgid, tid, sig)
        return

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<class '%s (pid: %s | name: %s)'>" % (self.__class__.__name__, 
                                                      self.pid, self.name)

