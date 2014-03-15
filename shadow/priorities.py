#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes


PRIO_PROCESS = ctypes.c_int(0)
PRIO_PGRP = ctypes.c_int(1)
PRIO_USER = ctypes.c_int(2)

IOPRIO_WHO_PROCESS = ctypes.c_int(1)
IOPRIO_WHO_PGRP = ctypes.c_int(2)
IOPRIO_WHO_USER = ctypes.c_int(3)

priority_classes = {0:'none', 
                    1:'realtime', 
                    2:'best-effort', 
                    3:'idle', 
                    4:'normal'}

IOPRIO_SHIFT = 13
IOPRIO_MASK_BASE = ctypes.c_ulong(1)
IOPRIO_MASK = (IOPRIO_MASK_BASE.value << IOPRIO_SHIFT) - 1

IOPRIO_PRIO_CLASS = lambda mask: mask >> IOPRIO_SHIFT
IOPRIO_PRIO_DATA = lambda mask: mask & IOPRIO_MASK

IOPRIO_GET = 290 #XXX will vary depending on architecture
                 # this value is for a i686 32bit system

libc = ctypes.CDLL('libc.so.6')

ioprio_get = lambda WHO, WHICH: libc.syscall(IOPRIO_GET, WHO, WHICH)
getpriority = lambda WHO, WHICH: libc.getpriority(WHO, WHICH)
setpriority = lambda WHO, WHICH, VALUE: libc.setpriority(WHO, WHICH, VALUE)

def ioprio_mask(who, pid):
    return ioprio_get(who, pid)

def ioprio_class(mask):
    return IOPRIO_PRIO_CLASS(mask)

def ioprio_data(mask):
    return IOPRIO_PRIO_DATA(mask)

def ioprio(which, who=IOPRIO_WHO_PROCESS):
    mask = ioprio_mask(who, which)
    io_class = priority_classes[ioprio_class(mask)]
    return (io_class, ioprio_data(mask))

def nice(which, who=PRIO_PROCESS):
    niceness = getpriority(who, which)
    return niceness

def setnice(which, level, who=PRIO_PROCESS):
    setpriority(who, which, level)
    return
