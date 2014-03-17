shadow
======

Module will create a `Profile` object from a any pid provided.  The object can
then be referenced to retrieve certain attributes of the process.

#### setup

Run the setup file with the `install` argument to install the shadow module:

    python setup.py install

Once installed, you can import `shadow` and/or `Profile`:

    >>> from shadow.shadow import Profile
    >>>
    >>> p = Profile(321) # 321 being a valid pid
    >>>

