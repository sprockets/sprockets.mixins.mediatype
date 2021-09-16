#!/usr/bin/env python
import pkg_resources
import setuptools

dist = pkg_resources.get_distribution('setuptools')
setup_version = tuple(int(c) for c in dist.version.split('.')[:3])
if setup_version < (42, 0):
    raise ImportError('Please upgrade setuptools')

setuptools.setup()
