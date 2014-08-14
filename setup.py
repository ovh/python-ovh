#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    setup_requires=['d2to1'],
    d2to1=True,
    tests_require=[
        "coverage==3.7.1",
        "mock==1.0.1",
        "nose==1.3.3",
        "yanc==0.2.4",
    ],
)

