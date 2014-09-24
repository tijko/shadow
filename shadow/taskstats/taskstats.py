#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This module sets a netlink connection, which will be used to communicate
the taskstats data to the shadowed PID's profile.
'''

import struct

from netlink import *
from ..exception import *
from controller import Controller, Genlmsg


# Taskstats commands
TASKSTATS_CMD_UNSPEC = 0
TASKSTATS_CMD_GET    = 1
TASKSTATS_CMD_NEW    = 2
_TASKSTATS_CMD_MAX   = 3

# Taskstats response types
TASKSTATS_TYPE_UNSPEC    = 0
TASKSTATS_TYPE_PID       = 1
TASKSTATS_TYPE_TGID      = 2
TASKSTATS_TYPE_STATS     = 3
TASKSTATS_TYPE_AGGR_PID  = 4
TASKSTATS_TYPE_AGGR_TGID = 5
TASKSTATS_TYPE_NULL      = 7
__TASKSTATS_TYPE_MAX     = 6

# Taskstats command attributes
TASKSTATS_CMD_ATTR_UNSPEC             = 0
TASKSTATS_CMD_ATTR_PID                = 1
TASKSTATS_CMD_ATTR_TGID               = 2 
TASKSTATS_CMD_ATTR_REGISTER_CPUMASK   = 3
TASKSTATS_CMD_ATTR_DEREGISTER_CPUMASK = 4
__TASKSTATS_CMD_ATTR_MAX              = 5

TASKSTATS_GENL_NAME    = 'TASKSTATS'

READ_ALIGNMENT  = 248
WRITE_ALIGNMENT = 256


class Taskstats(object):
    '''
    The Taskstats class makes requests to assemble netlink messages that
    communicate taskstats.
    '''
    def __init__(self, pid):
        super(Taskstats, self).__init__()
        self.pid = pid
        self.genlctrl = Controller(TASKSTATS_GENL_NAME)
        self.attrs = dict()

    def get(self):
        task_msg_payload = Genlmsg(TASKSTATS_CMD_GET, Nlattr(
                                   TASKSTATS_CMD_ATTR_PID, self.pid))
        self.genlctrl.send(Nlmsg(self.genlctrl.fam_id, task_msg_payload).pack())
        task_response = self.genlctrl.recv()
        parse_response(self, task_response[NLA_HDRLEN:])
        return self.attrs[TASKSTATS_TYPE_STATS]
    
    def read(self):
        taskstats = self.get()
        return struct.unpack('Q', taskstats[READ_ALIGNMENT:READ_ALIGNMENT + 8])

    def write(self):
        taskstats = self.get()
        return struct.unpack('Q', taskstats[WRITE_ALIGNMENT:WRITE_ALIGNMENT + 8])
