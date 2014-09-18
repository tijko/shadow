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

NLMSG_ALIGNTO   = 4

NLMSG_MIN_TYPE  = 0x10
NLMSG_ERROR     = 0x2

GENL_ID_CTRL = NLMSG_MIN_TYPE


class Nlmsg(dict):
    '''
    The Nlmsghdr class handles the assembly of netlink headers and encapsulation
    of the associated fields.
    '''
    NLMSG_HDRLEN = struct.calcsize('IHHII')

    def __init__(self, nlmsg_type, genlmsg):
        super(Nlmsg, self).__init__()
        self.fields = ['nl_len', 'nl_type', 'nl_flags', 'nl_seq', 'nl_pid']
        self['nl_pid'] = os.getpid()
        self['nl_flags'] = NLM_F_REQUEST
        self['nl_len'] = Nlmsg.NLMSG_HDRLEN 
        self['nl_type'] = nlmsg_type
        self['nl_seq'] = 0
        self.genlmsg = genlmsg
        
    def pack(self):
        self['nl_len'] += self.genlmsg.genlen 
        nlmsghdr = struct.pack('IHHII', *[self[field] for field in self.fields])
        return nlmsghdr + self.genlmsg.pack()


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


class Nlattr(object):
    '''
    The Nlattr class handles the assembly of netlink-attributes headers and 
    encapsulation of the associated fields.
    '''
    NLA_HDRLEN = struct.calcsize('HH')

    def __init__(self, nla_type, nla_data):
        self.nla_type = nla_type
        self.nla_data = nla_data
        self.nla_len = Nlattr.NLA_HDRLEN

    def pack(self):
        nla_payload = self.payload
        nla_hdr = struct.pack('HH', self.nla_len, self.nla_type)
        return nla_hdr + nla_payload

    @property
    def payload(self):
        load = ''
        if isinstance(self.nla_data, str):
            padding = calc_alignment(len(self.nla_data))
            self.nla_len += padding
            load = struct.pack('%ds' % padding, self.nla_data)
        elif isinstance(self.nla_data, int):
            self.nla_len += calc_alignment(struct.calcsize('I'))
            load = struct.pack('I', self.nla_data)
        return load


def calc_alignment(data):
    return ((data + NLMSG_ALIGNTO - 1) & ~(NLMSG_ALIGNTO - 1))
