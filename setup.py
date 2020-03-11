#!/usr/bin/env python
import pathlib
import setuptools

from sprockets.mixins import mediatype

REPO_DIR = pathlib.Path(__name__).parent


def read_requirements(name):
    requirements = []
    for req_line in REPO_DIR.joinpath(name).read_text().split('\n'):
        req_line = req_line.strip()
        if '#' in req_line:
            req_line = req_line[0:req_line.find('#')].strip()
        if req_line.startswith('-r'):
            req_line = req_line[2:].strip()
            requirements.extend(read_requirements(req_line))
        else:
            requirements.append(req_line)
    return requirements


setuptools.setup(
    name='sprockets.mixins.mediatype',
    version=mediatype.__version__,
    description='A mixin for reporting handling content-type/accept headers',
    long_description=REPO_DIR.joinpath('README.rst').read_text(),
    url='https://github.com/sprockets/sprockets.mixins.mediatype',
    author='AWeber Communications',
    author_email='api@aweber.com',
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=setuptools.find_packages(),
    install_requires=read_requirements('requires/installation.txt'),
    tests_require=read_requirements('requires/testing.txt'),
    extras_require={
        'msgpack': ['msgpack>=1,<2']
    },
    namespace_packages=['sprockets', 'sprockets.mixins'],
    test_suite='nose.collector',
    python_requires='>=3.7',
    zip_safe=False)
