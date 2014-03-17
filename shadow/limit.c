#include <Python.h>
#include <sys/resource.h>


static PyObject *limit_getlimit(PyObject *self, PyObject *args)
{
    int pid, resource;
    struct rlimit *new = NULL;
    struct rlimit *old = malloc(sizeof *old);
    if (!PyArg_ParseTuple(args, "ii", &pid, &resource)) {
        return NULL;
    }

    int ret = prlimit(pid, resource, new, old);
    if (ret < 0) {
        return NULL;
    }
    return Py_BuildValue("l", old->rlim_cur);
}

static PyMethodDef limitmethods[] = {
    {"getlimit", limit_getlimit, METH_VARARGS, "return current resource limits."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initlimit(void)
{
    PyObject *limitmod = Py_InitModule("limit", limitmethods);
    PyModule_AddIntConstant(limitmod, "RLIMIT_AS", RLIMIT_AS);
    PyModule_AddIntConstant(limitmod, "RLIMIT_CORE", RLIMIT_CORE);
    PyModule_AddIntConstant(limitmod, "RLIMIT_CPU", RLIMIT_CPU);
    PyModule_AddIntConstant(limitmod, "RLIMIT_DATA", RLIMIT_DATA);
    PyModule_AddIntConstant(limitmod, "RLIMIT_FSIZE", RLIMIT_FSIZE);
    PyModule_AddIntConstant(limitmod, "RLIMIT_LOCKS", RLIMIT_LOCKS);
    PyModule_AddIntConstant(limitmod, "RLIMIT_MEMLOCK", RLIMIT_MEMLOCK);
    PyModule_AddIntConstant(limitmod, "RLIMIT_MSGQUEUE", RLIMIT_MSGQUEUE);
    PyModule_AddIntConstant(limitmod, "RLIMIT_NICE", RLIMIT_NICE);
    PyModule_AddIntConstant(limitmod, "RLIMIT_NOFILE", RLIMIT_NOFILE);
    PyModule_AddIntConstant(limitmod, "RLIMIT_NPROC", RLIMIT_NPROC);
    PyModule_AddIntConstant(limitmod, "RLIMIT_RSS", RLIMIT_RSS);
    PyModule_AddIntConstant(limitmod, "RLIMIT_RTTIME", RLIMIT_RTTIME);
    PyModule_AddIntConstant(limitmod, "RLIMIT_SIGPENDING", RLIMIT_SIGPENDING);
    PyModule_AddIntConstant(limitmod, "RLIMIT_STACK", RLIMIT_STACK);
}
