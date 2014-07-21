#include <Python.h>

#include "libshadow.h"


static PyObject *ShadowErr;

static PyObject *libshadow_curlimit(PyObject *self, PyObject *args)
{
    int pid, resource;
    struct rlimit *new = NULL;
    struct rlimit *old = malloc(sizeof *old);
    if (!PyArg_ParseTuple(args, "ii", &pid, &resource)) {
        return NULL;
    }
    int ret = prlimit(pid, resource, new, old);
    if (ret < 0) {
        PyErr_SetString(ShadowErr, strerror(errno));
        return NULL;
    }
    return Py_BuildValue("l", old->rlim_cur);
}

static PyObject *libshadow_maxlimit(PyObject *self, PyObject *args)
{
    int pid, resource;
    struct rlimit *new = NULL;
    struct rlimit *old = malloc(sizeof *old);
    if (!PyArg_ParseTuple(args, "ii", &pid, &resource)) {
        return NULL;
    }
    int ret = prlimit(pid, resource, new, old);
    if (ret < 0) {
        PyErr_SetString(ShadowErr, strerror(errno));
        return NULL;
    }
    return Py_BuildValue("l", old->rlim_max);
}

static PyObject *libshadow_isoproc(PyObject *self, PyObject *args)
{
    int pid, ret, i;
    cpu_set_t isopid;
    cpu_set_t aotpid;
    CPU_ZERO(&isopid);
    CPU_ZERO(&aotpid);
    size_t isosize = CPU_ALLOC_SIZE(1);
    size_t aotsize = CPU_ALLOC_SIZE(NPROC - 1);
    if (!PyArg_ParseTuple(args, "i", &pid)) {
        return NULL;
    }
    if  (NPROC <= 1) {
        return NULL;
    }
    CPU_SET(0, &isopid);
    ret = sched_setaffinity(pid, isosize, &isopid);
    if (ret < 0) {
        PyErr_SetString(ShadowErr, strerror(errno));
    }
    for (i=1; i < NPROC; i++) { 
        CPU_SET(i, &aotpid);
    }
    aotcpu(pid, aotsize, aotpid);
    Py_RETURN_NONE;
}

int procek(char *dirname)
{
    char *procptr;
    strtod(dirname, &procptr);
    return *procptr == '\0';
}

int aotcpu(int isopid, size_t aotsize, cpu_set_t aotpid)
{
    int proc, ret;
    char *base = "/proc/";
    DIR *dir = opendir(base);
    struct dirent *cdir = malloc(sizeof *cdir);
    while ((cdir = readdir(dir))) {
        if (cdir->d_type == DT_DIR && procek(cdir->d_name)) {
            proc = strtol(cdir->d_name, NULL, 10);
            if (proc != isopid) {
                ret = sched_setaffinity(proc, aotsize, &aotpid);
            }
        }
    }
    closedir(dir);
    return 0;
}

static PyObject *libshadow_relproc(PyObject *self, PyObject *args)
{
    int pid, i;
    if (!PyArg_ParseTuple(args, "i", &pid)) {
        return NULL;
    }
    cpu_set_t allproc;
    CPU_ZERO(&allproc);
    for (i=0; i < NPROC; i++) {
        CPU_SET(i, &allproc);
    }
    size_t allsize = CPU_ALLOC_SIZE(NPROC);
    aotcpu(0, sizeof allsize, allproc);
    Py_RETURN_NONE;
}

static PyObject *libshadow_procaff(PyObject *self, PyObject *args)
{
    int pid, ret, affinity;
    cpu_set_t cpumask;
    if (!PyArg_ParseTuple(args, "i", &pid)) {
        return NULL;
    }
    ret = sched_getaffinity(pid, sizeof cpumask, &cpumask);
    if (ret < 0) {
        PyErr_SetString(ShadowErr, strerror(errno));
        return NULL;
    }
    affinity = CPU_COUNT(&cpumask);
    Py_BuildValue("i", affinity);
}

static PyMethodDef libshadowmethods[] = {
    {"curlimit", libshadow_curlimit, METH_VARARGS, 
     "return current resource limits."},
    {"maxlimit", libshadow_maxlimit, METH_VARARGS,
     "return max resource limits."},
    {"isoproc", libshadow_isoproc, METH_VARARGS,
     "isolate process to run on one core."},
    {"relproc", libshadow_relproc, METH_VARARGS,
     "release isolated process."},
    {"procaff", libshadow_procaff, METH_VARARGS,
     "return process affinity."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initlibshadow(void)
{
    PyObject *shadowmod = Py_InitModule("libshadow", libshadowmethods);
    PyModule_AddIntConstant(shadowmod, "RLIMIT_AS", RLIMIT_AS);
    PyModule_AddIntConstant(shadowmod, "RLIMIT_CORE", RLIMIT_CORE);
    PyModule_AddIntConstant(shadowmod, "RLIMIT_CPU", RLIMIT_CPU);
    PyModule_AddIntConstant(shadowmod, "RLIMIT_DATA", RLIMIT_DATA);
    PyModule_AddIntConstant(shadowmod, "RLIMIT_FSIZE", RLIMIT_FSIZE);
    PyModule_AddIntConstant(shadowmod, "RLIMIT_LOCKS", RLIMIT_LOCKS);
    PyModule_AddIntConstant(shadowmod, "RLIMIT_MEMLOCK", RLIMIT_MEMLOCK);
    PyModule_AddIntConstant(shadowmod, "RLIMIT_MSGQUEUE", RLIMIT_MSGQUEUE);
    PyModule_AddIntConstant(shadowmod, "RLIMIT_NICE", RLIMIT_NICE);
    PyModule_AddIntConstant(shadowmod, "RLIMIT_NOFILE", RLIMIT_NOFILE);
    PyModule_AddIntConstant(shadowmod, "RLIMIT_NPROC", RLIMIT_NPROC);
    PyModule_AddIntConstant(shadowmod, "RLIMIT_RSS", RLIMIT_RSS);
    PyModule_AddIntConstant(shadowmod, "RLIMIT_RTTIME", RLIMIT_RTTIME);
    PyModule_AddIntConstant(shadowmod, "RLIMIT_SIGPENDING", RLIMIT_SIGPENDING);
    PyModule_AddIntConstant(shadowmod, "RLIMIT_STACK", RLIMIT_STACK);
    ShadowErr = PyErr_NewException("libshadow.error", NULL, NULL);
    Py_INCREF(ShadowErr);
    PyModule_AddObject(shadowmod, "error", ShadowErr);
}
