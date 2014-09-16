#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This module sets a netlink connection, which will be used to communicate
the taskstats data to shadowed PID's profile.
'''

import socket
import struct
import os

from exceptions import *


# Flag values
NLM_F_REQUEST   = 1
NLM_F_MULTI     = 2
NLM_F_ACK       = 4
NLM_F_ECHO      = 8
NLM_F_DUMP_INTR = 16

# Modifiers to GET request
NLM_F_ROOT      = 0x100
NLM_F_MATCH     = 0x200
NLM_F_ATOMIC    = 0x400
NLM_F_DUMP      = (NLM_F_ROOT | NLM_F_MATCH)

# Modifiers to NEW requests
NLM_F_REPLACE   = 0x100
NLM_F_EXCL      = 0x200
NLM_F_CREATE    = 0x400
NLM_F_APPEND    = 0x800

# Genetlink Controller command and attribute values
CTRL_CMD_UNSPEC       = 0
CTRL_CMD_NEWFAMILY    = 1
CTRL_CMD_DELFAMILY    = 2
CTRL_CMD_GETFAMILY    = 3 
CTRL_CMD_NEWOPS       = 4
CTRL_CMD_DELOPS       = 5
CTRL_CMD_GETOPS       = 6
CTRL_CMD_NEWMCAST_GRP = 7
CTRL_CMD_DELMCAST_GRP = 8
CTRL_CMD_GETMCAST_GRP = 9
__CTRL_CMD_MAX        = 10

CTRL_ATTR_UNSPEC       = 0
CTRL_ATTR_FAMILY_ID    = 1
CTRL_ATTR_FAMILY_NAME  = 2
CTRL_ATTR_VERSION      = 3
CTRL_ATTR_HDRSIZE      = 4
CTRL_ATTR_MAXATTR      = 5
CTRL_ATTR_OPS          = 6
CTRL_ATTR_MCAST_GROUPS = 7
__CTRL_ATTR_MAX        = 8

CTRL_ATTR_OP_UNSPEC = 0
CTRL_ATTR_OP_ID     = 1
CTRL_ATTR_OP_FLAGS  = 2
__CTRL_ATTR_OP_MAX  = 3

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

TASKSTATS_GENL_NAME = 'TASKSTATS'

#XXX These definitions are from 3.16.0


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
    
    
NETLINK_GENERIC = 16
NLMSG_ALIGNTO   = 4

NLMSG_MIN_TYPE  = 0x10
NLMSG_ERROR     = 0x2

GENL_ID_CTRL = NLMSG_MIN_TYPE


class NetlinkMessage(Connection):


    '''
    The NetlinkMessage class handles the assembly of netlink headers.
    '''
    def __init__(self):
        super(NetlinkMessage, self).__init__()
        self.pid = os.getpid()
        self.flags = NLM_F_REQUEST
        self.genl_version = 0

    def get_family_id(self, family_name):
        nlattr, nla_len = self.build_nlattr(CTRL_ATTR_FAMILY_NAME, family_name)
        genl_hdr, genl_len = self.build_genlmsghdr(CTRL_CMD_GETFAMILY)
        ntpayload_len = nla_len + genl_len
        nlmsg_hdr = self.build_nlmsghdr(GENL_ID_CTRL, ntpayload_len)
        fam_req = ''.join([nlmsg_hdr, genl_hdr, nlattr])
        self.send(fam_req)
        return self.recv()

    def build_nlmsghdr(self, nlmsg_type, nlmsg_len):
        seq = 0
        nlmsg_len += struct.calcsize('IHHII')
        hdr = [nlmsg_len, nlmsg_type, self.flags, seq, self.pid]
        nlmsghdr = struct.pack('IHHII', *hdr)
        return nlmsghdr

    def build_genlmsghdr(self, cmd):
        genlhdr = struct.pack('BBxx', cmd, self.genl_version)
        genl_len = struct.calcsize('BBxx')
        return genlhdr, genl_len

    def build_nlattr(self, nla_type, nla_data):
        if isinstance(nla_data, str):
            padding = self.calc_alignment(nla_data)
            nla_len = struct.calcsize('HH') + padding
            nla_hdr = struct.pack('HH', nla_len, nla_type)
            data  = struct.pack('%ds' % padding, nla_data)
            nlattr = b''.join([nla_hdr, data])
        elif isinstance(nla_data, int):
            nla_len = struct.calcsize('HHI')
            nla = [nla_len, nla_type, nla_data]
            nlattr = struct.pack('HHI', *nla)
        else:
            return [], 0
        return nlattr, nla_len

    def calc_alignment(self, data):
        return ((len(data) + NLMSG_ALIGNTO - 1) & ~(NLMSG_ALIGNTO - 1))

    def parse_msg(self, msg):
        nl_len, nl_type = struct.unpack('IHHII', msg[:16])[:2]
        if nl_type == NLMSG_ERROR:
            raise NetlinkError(self.parse_msg.func_name, self.pid)
        nlattrs = msg[20:]
        attributes = dict()
        while (nlattrs):
            nla_len, nla_type = map(int, struct.unpack('HH', nlattrs[:4]))
            nla_len = self.calc_alignment(nlattrs[:nla_len])
            nla_data = nlattrs[4:nla_len]
            attributes[nla_type] = nla_data
            nlattrs = nlattrs[nla_len:]
        return attributes 


class Taskstats(NetlinkMessage):
    '''
    The main class which calls makes request through NetLinkMessage to
    communicate taskstats.
    '''
    def __init__(self):
        super(Taskstats, self).__init__()
        self.family_id = None

    def taskstats_family_id(self):
        family_id_reply = self.get_family_id(TASKSTATS_GENL_NAME)
        self.family_id = self.parse_msg(family_id_reply)
        return struct.unpack('I', self.family_id[CTRL_ATTR_FAMILY_ID])[0]
