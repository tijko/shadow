#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This module sets up and handles the netlink communication.  Once the netlink
connection is established, the socket connection will remain open for the 
duration of the process being shadowed.  Each message requested is built,  
parsed, and routed through these local functions.   
'''

import socket
import struct

from exception import *


'''
Constants and flags used for creating usable netlink messages
'''
 
NLMSG_ERROR = 0x2 
NLMSG_VERSION= 0x10
CTRL_CMD_GETFAMILY = 0x3
NLM_F_REQUEST = 0x1
CTRL_ATTR_FAMILY_ID = 0x1
TASKSTATS_CMD_GET = 0x1
TASKSTATS_CMD_ATTR_PID = 0x1
TASKSTATS_TYPE_AGGR_PID = 0x4
TASKSTATS_TYPE_STATS = 0x3
NLM_OFFSET = 0x14
NLM_R_ST = 0xf8
NLM_R_EN = 0x100
NLM_W_ST = 0x100
NLM_W_EN = 0x108
FAMILY_SEQ = 0x0
OPT_VAL = 0xffff
PAD_MASK = 0b11
HDR_ALG = 0b11
HDR_PAD = 0x4
NLMSG_PAD = 0x4
NTLNK_BUF = 0x10
NTLNK_GENR = 0x10


class __NetLinkConn(object):
    '''
    Base class to establish a netlink socket connection and signal message
    request to userspace for a given process
    '''
    def __init__(self):
        self.__conn = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, NTLNK_GENR)
        self.__conn.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, OPT_VAL)
        self.__conn.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, OPT_VAL)
        self.__conn.bind((0,0))
        self.__pid, self.__grp = self.__conn.getsockname()

    def _ntlnk_exchange(self):
        read, write = gentlnk_taskstat(self.__conn, self.__pid, self.pid)
        return read, write


r_segment = lambda m: m[NLM_R_ST:NLM_R_EN]
w_segment = lambda m: m[NLM_W_ST:NLM_W_EN]

def build_ntlnk_payload(nl_type, flags):
    return struct.pack('BBxx', nl_type, flags)

def build_ntlnk_hdr(conn_pid, version, flags, seq, payload):
    length = len(payload)
    hdr = struct.pack('IHHII', length + NTLNK_BUF, version, flags, seq, conn_pid)
    return hdr
  
def build_padding(load):
    pad = ((len(load) + HDR_ALG) & ~PAD_MASK) - len(load)
    return pad

def get_family_name(conn, conn_pid, pid):
    payload = b''.join([build_ntlnk_payload(CTRL_CMD_GETFAMILY, FAMILY_SEQ)])
    gen_id = struct.pack('%dsB' % len('TASKSTATS'), 'TASKSTATS', 0)
    pad = build_padding(gen_id)
    genhdr = struct.pack('HH', len(gen_id) + HDR_PAD, 2)
    payload += b''.join([genhdr, gen_id, b'\0' * pad])
    hdr = build_ntlnk_hdr(conn_pid, NTLNK_GENR, NLM_F_REQUEST, FAMILY_SEQ + 1, payload) 
    conn.send(hdr + payload)
    ntlink_response = conn.recvfrom(16384)[0]
    taskstat_cmd = parse_msg(pid, ntlink_response[NLM_OFFSET:])[1]
    taskstat_cmd = struct.unpack('H', taskstat_cmd)[0]
    return taskstat_cmd

def parse_msg(pid, ntlink_msg):
    msg_segments = dict()
    while ntlink_msg:
        try:
            seg_len, seg_type = struct.unpack('HH', ntlink_msg[:NLMSG_PAD])
            msg_segments[seg_type] = ntlink_msg[NLMSG_PAD:seg_len]
            seg_len = ((seg_len + HDR_ALG) & ~PAD_MASK)
            ntlink_msg = ntlink_msg[seg_len:]
        except struct.error:
            raise StructParseError(parse_msg.func_name, pid)
    return msg_segments

def gentlnk_taskstat(conn, conn_pid, pid):
    ntlnk_family = get_family_name(conn, conn_pid, pid)
    payload = b''.join([build_ntlnk_payload(TASKSTATS_CMD_GET, 0)])
    gen_id = struct.pack('I', pid)
    pad = build_padding(gen_id)
    genhdr = struct.pack('HH', len(gen_id) + HDR_PAD, 1)
    payload += b''.join([genhdr, gen_id, b'\0' * pad])
    hdr = build_ntlnk_hdr(conn_pid, ntlnk_family, NLM_F_REQUEST, 
                          FAMILY_SEQ + 2, payload)
    conn.send(hdr + payload)
    ntlink_response = conn.recvfrom(16384)[0]
    msg_type = struct.unpack('H', ntlink_response[4:6])[0]
    if msg_type == NLMSG_ERROR:
        errno = struct.unpack('i', ntlink_response[16:20])[0]
        raise NetlinkError(errno, pid)
    segments = parse_msg(pid, ntlink_response[NLM_OFFSET:])
    if not segments.get(4):
        raise StructParseError(gentlnk_taskstats.func_name, pid) 
    ntlink_msg = parse_msg(pid, segments[4])[3]
    try:
        pid_read = struct.unpack('Q', r_segment(ntlink_msg))[0]
        pid_write = struct.unpack('Q', w_segment(ntlink_msg))[0]
    except struct.error:
        raise StructParseError(gentlnk_taskstats.func_name, pid)
    return (pid_read, pid_write)
