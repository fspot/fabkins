#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
This is a deploying job for my new project.

Usage:
    $ fab  # perform the deploy with default values
    $ fab say_hello:google  # deploy on google app engine
"""

from fabric.api import *

@task(default=True)
def say_hello(to="world"):
    """ deploy the project """
    print "Hello, %s!" % to

