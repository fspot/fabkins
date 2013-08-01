#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os


WEB_PORT = 8010
WORKDIR = "/home/fred/fabkinsdir"
PREFIX = "/fabkins"
PASSWORD = '\x07\x12>\x1fH#V\xc4\x15\xf6\x84@z;\x87#\xe1\x0b,\xbb\xc0\xb8\xfc\xd6(,I\xd3|\x9c\x1a\xbc'

TCP_PORT = 8011
SECRET_KEY = "sshhh"
DEBUG = True
TCP_CLIENT_TIMEOUT = 5

DEFAULT_FABFILE = '''#!/usr/bin/env python
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
'''
