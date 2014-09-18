#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This module sets a netlink connection, which will be used to communicate
the taskstats data to shadowed PID's profile.
'''

import struct

from netlink import *
from ..exception import *
from controller import Controller


# Taskstats commands
TASKSTATS_CMD_UNSPEC = 0
TASKSTATS_CMD_GET    = 1
TASKSTATS_CMD_NEW    = 2
_TASKSTATS_CMD_MAX   = 3

TASKSTATS_TYPE_UNSPEC    = 0
TASKSTATS_TYPE_PID       = 1
TASKSTATS_TYPE_TGID      = 2
TASKSTATS_TYPE_STATS     = 3
TASKSTATS_TYPE_AGGR_PID  = 4
TASKSTATS_TYPE_AGGR_TGID = 5
TASKSTATS_TYPE_NULL      = 7
__TASKSTATS_TYPE_MAX     = 6

TASKSTATS_CMD_ATTR_UNSPEC             = 0
TASKSTATS_CMD_ATTR_PID                = 1
TASKSTATS_CMD_ATTR_TGID               = 2 
TASKSTATS_CMD_ATTR_REGISTER_CPUMASK   = 3
TASKSTATS_CMD_ATTR_DEREGISTER_CPUMASK = 4
__TASKSTATS_CMD_ATTR_MAX              = 5

TASKSTATS_GENL_NAME    = 'TASKSTATS'
TASKSTATS_GENL_VERSION = 0x1


class Taskstats(object):
    '''
    The Taskstats class makes requests to assemble netlink messages that
    communicate taskstats.
    '''
    def __init__(self, pid):
        super(Taskstats, self).__init__()
        self.family_id = None
        self.pid = pid
        self.genlctrl = Controller(TASKSTATS_GENL_VERSION, TASKSTATS_GENL_NAME)

    def taskstats_family_id(self):
        family_id_response = self.genlctrl.family_id()
        return self.parse_msg(family_id_response)
        
    def parse_msg(self, msg):
        nl_len, nl_type = struct.unpack('IHHII', msg[:16])[:2]
        if nl_type == NLMSG_ERROR:
            raise NetlinkError(self.parse_msg.func_name, self.pid)
        nlattrs = msg[20:]
        attributes = dict()
        while (nlattrs):
            nla_len, nla_type = map(int, struct.unpack('HH', nlattrs[:4]))
            nla_len = calc_alignment(nlattrs[:nla_len])
            nla_data = nlattrs[4:nla_len]
            attributes[nla_type] = nla_data
            nlattrs = nlattrs[nla_len:]
        return attributes
