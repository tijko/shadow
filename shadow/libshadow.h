#include <sched.h>
#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/resource.h>


#define NPROC sysconf(_SC_NPROCESSORS_ONLN)

int procek(char *dirname);

int aotcpu(int isopid, size_t aotsize, cpu_set_t aotpid);
