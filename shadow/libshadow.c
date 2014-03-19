#include <Python.h>
#include <sched.h>
#include <errno.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/resource.h>

#include "cpu.h"


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

static PyObject *libshadow_getcpu(PyObject *self, PyObject *args)
{
    int pid, cpu;
    int GETCPU = 318;
    if (!PyArg_ParseTuple(args, "i", &pid)) {
        return NULL;
    }
    int ret = syscall(GETCPU, &cpu, &pid, NULL);
    if (ret < 0) {
        PyErr_SetString(ShadowErr, strerror(errno));
        return NULL;
    }
    return Py_BuildValue("i", cpu);
}

static PyMethodDef libshadowmethods[] = {
    {"curlimit", libshadow_curlimit, METH_VARARGS, 
     "return current resource limits."},
    {"maxlimit", libshadow_maxlimit, METH_VARARGS,
     "return max resource limits."},
    {"getcpu", libshadow_getcpu, METH_VARARGS,
     "return the processor the process is running on."},
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
