#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension


setup( 
    name = 'shadow',
    version = '0.0.1',
    author='Tim Konick',
    author_email='konick781@gmail.com',
    url='',
    description='Provides auxillary data on processes',
    long_description=open('README.md').read(),
    license=open('LICENSE').read(),
    packages=['shadow'],
    ext_modules=[Extension('libshadow', sources=['shadow/libshadow/libshadow.c'])]
)
