#!/usr/bin/env python
#

import os
import setuptools


def read_requirements(file_name):
    requirements = []
    try:
        with open(os.path.join('requires', file_name)) as req_file:
            for req_line in req_file:
                req_line = req_line.strip()
                if '#' in req_line:
                    req_line = req_line[0:req_line.find('#')].strip()
                if req_line.startswith('-r'):
                    req_line = req_line[2:].strip()
                    requirements.extend(read_requirements(req_line))
                else:
                    requirements.append(req_line)
    except IOError:
        pass
    return requirements


install_requires = read_requirements('installation.txt')
tests_require = read_requirements('testing.txt')

setuptools.setup(
    name='sprockets.mixins.mediatype',
    version='1.0.4',
    description='A mixin for reporting handling content-type/accept headers',
    long_description='\n' + open('README.rst').read(),
    url='https://github.com/sprockets/sprockets.mixins.media_type',
    author='AWeber Communications',
    author_email='api@aweber.com',
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'msgpack': ['u-msgpack-python>=2.1,<3'],
    },
    namespace_packages=['sprockets', 'sprockets.mixins'],
    test_suite='nose.collector',
    zip_safe=False)
