#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages
import fabkins

setup(
    name='fabkins',
    version=fabkins.__version__,
    install_requires=["Fabric", "Flask", "gevent-websocket", "clize"],
    packages=find_packages(),
    author="fspot",
    author_email="fred@fspot.org",
    description="Fabkins, a femto-jenkins based on fabfiles",
    long_description=''.join(open('README.md').readlines()[:16]),
    include_package_data=True,
    zip_safe=False,
    url='http://github.com/fspot/fabkins',
    entry_points = {
        'console_scripts': [
            'fabkins = fabkins.app:main_entry_point',
            'fabkins-patch-venv = fabkins.patch:main_entry_point',
            'fabkins-gen-conf = fabkins.gen:conf_entry_point',
            'fabkins-gen-static = fabkins.gen:static_entry_point',
        ],
    },
    license='MIT',
)

