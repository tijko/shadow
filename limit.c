#include <Python.h>
#include <unistd.h>
#include <sys/time.h>
#include <sys/resource.h>


static PyObject *getlimit(PyObject *self, PyObject *args)
{
    int pid, resource;
    struct rlimit *cur = malloc(sizeof *cur);
    struct rlimit *max = NULL;
    if (!PyArg_ParseTuple(args, "ii", &pid, &resource))
        return NULL;
    int ret = prlimit(pid, resource, max, cur);
    if (ret < 0)
        return NULL;
    printf("%u\n", cur->rlim_cur);
    Py_RETURN_NONE;
}

static PyMethodDef GetLimit[] = {
    {"getlimit", getlimit, METH_VARARGS, "return current resource limits."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initlimit(void)
{
    (void) Py_InitModule("limit", GetLimit);
}        
