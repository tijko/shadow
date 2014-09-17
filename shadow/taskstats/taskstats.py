#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This module sets a netlink connection, which will be used to communicate
the taskstats data to shadowed PID's profile.
'''

import socket
import struct

from netlink import *
from ..exception import *


class Connection(object):
    '''
    Base class that establishes a netlink connection with the kernel.
    '''
    def __init__(self):
        self.conn = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, 
                                                      NETLINK_GENERIC)
        self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
        self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        self.conn.bind((0, 0))

    def send(self, msg):
        self.conn.send(msg)

    def recv(self):
        return self.conn.recv(65536)

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


class Taskstats(Connection):
    '''
    The Taskstats class makes requests to assemble netlink messages that
    communicate taskstats.
    '''
    def __init__(self):
        super(Taskstats, self).__init__()
        self.family_id = None

    def taskstats_family_id(self):
        self.nlmsghdr = Nlmsghdr(GENL_ID_CTRL)         
        self.genlmsghdr = Genlmsghdr(CTRL_CMD_GETFAMILY, TASKSTATS_GENL_VERSION)
        self.nlattr = Nlattr(CTRL_ATTR_FAMILY_NAME, TASKSTATS_GENL_NAME)
        self.nlmsghdr.build_hdr()
        self.genlmsghdr.build_hdr()
        self.nlattr.build_nlattr() 
#
#        self.family_id = self.parse_msg(family_id_reply)
#        return struct.unpack('I', self.family_id[CTRL_ATTR_FAMILY_ID])[0]
        
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