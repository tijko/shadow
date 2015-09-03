#ifndef SHADOW_H
#define SHADOW_H

#include <Python.h>

#include <sched.h>
#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <signal.h>
#include <sys/syscall.h>
#include <sys/resource.h>


#define NPROC sysconf(_SC_NPROCESSORS_ONLN)

#define PROC_DIR "/proc/"
 

#ifdef __x86_64__
#define TGKILL_CALL 234
#elif __i386__
#define TGKILL_CALL 270
#endif

int procek(char *dirname);

int aothcpu(int isopid, size_t aothset_size, cpu_set_t aothset);

#endif
