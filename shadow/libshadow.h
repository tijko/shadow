
#include <unistd.h>

#define NPROC sysconf(_SC_NPROCESSORS_ONLN)

int procek(char *dirname);

int aotcpu(int isopid, size_t aotsize, cpu_set_t aotpid);
