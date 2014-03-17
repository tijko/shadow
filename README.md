shadow
======

Module will create a `Profile` object from a any pid provided.  The object can
then be referenced to retrieve certain attributes of the process.

#### description

The `Profile` class is subclassed from `__NetLinkConn` in the `connection.py` 
file. This base class sets up a linux netlink connection that handles the 
communication of the processes input/output.

    >>> from shadow.shadow import Profile
    >>>
    >>> p = Profile(321) #321 being a valid pid
    >>>

#### setup

Run the setup file from a terminal with the `install` argument to install the 
shadow module:

    python setup.py install

