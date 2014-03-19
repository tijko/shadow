/* 
 * Macro to set the correct system call number for 
 * getcpu, as the linux api doesn't provide a wrapper
 * for the call.
 */

#ifdef __x86_64__
#define GETCPU 309
#elif __i386__
#define GETCPU 318
#endif
