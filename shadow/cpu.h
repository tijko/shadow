/* set getcpu syscall based on architecture */

#ifdef __x86_64__
#define GETCPU 309
#elif __i386__
#define GETCPU 318
#endif

#include <unistd.h>

#define NPROC sysconf(_SC_NPROCESSORS_ONLN)

int procek(char *dirname);

int aotcpu(int isopid, size_t aotsize, cpu_set_t aotpid);
