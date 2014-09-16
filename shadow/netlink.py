#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import os


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

NETLINK_GENERIC = 16
NLMSG_ALIGNTO   = 4

NLMSG_MIN_TYPE  = 0x10
NLMSG_ERROR     = 0x2

GENL_ID_CTRL = NLMSG_MIN_TYPE


class Nlmsghdr(object):
    '''
    The NetlinkMessage class handles the assembly of netlink headers.
    '''
    def __init__(self):
        super(NetlinkMessage, self).__init__()
        self.pid = os.getpid()
        self.flags = NLM_F_REQUEST
        self.genl_version = 0
        
    def build_nlmsghdr(self, nlmsg_type, nlmsg_len):
        seq = 0
        nlmsg_len += struct.calcsize('IHHII')
        hdr = [nlmsg_len, nlmsg_type, self.flags, seq, self.pid]
        nlmsghdr = struct.pack('IHHII', *hdr)
        return nlmsghdr
        
# Genetlink Controller command and attribute values
CTRL_CMD_UNSPEC        = 0
CTRL_CMD_NEWFAMILY     = 1
CTRL_CMD_DELFAMILY     = 2
CTRL_CMD_GETFAMILY     = 3 
CTRL_CMD_NEWOPS        = 4
CTRL_CMD_DELOPS        = 5
CTRL_CMD_GETOPS        = 6
CTRL_CMD_NEWMCAST_GRP  = 7
CTRL_CMD_DELMCAST_GRP  = 8
CTRL_CMD_GETMCAST_GRP  = 9
__CTRL_CMD_MAX         = 10

CTRL_ATTR_UNSPEC       = 0
CTRL_ATTR_FAMILY_ID    = 1
CTRL_ATTR_FAMILY_NAME  = 2
CTRL_ATTR_VERSION      = 3
CTRL_ATTR_HDRSIZE      = 4
CTRL_ATTR_MAXATTR      = 5
CTRL_ATTR_OPS          = 6
CTRL_ATTR_MCAST_GROUPS = 7
__CTRL_ATTR_MAX        = 8

CTRL_ATTR_OP_UNSPEC    = 0
CTRL_ATTR_OP_ID        = 1
CTRL_ATTR_OP_FLAGS     = 2
__CTRL_ATTR_OP_MAX     = 3
        

class Genlmsghdr(object):

    def __init__(self):
        pass

    def build_genlmsghdr(self, cmd):
        genlhdr = struct.pack('BBxx', cmd, self.genl_version)
        genl_len = struct.calcsize('BBxx')
        return genlhdr, genl_len


class Nlattr(object):

    def __init__(self):
        pass

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
