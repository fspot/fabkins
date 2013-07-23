#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os


WEB_PORT = 8010
WORKDIR = "/home/fred/fabkinsdir"

TCP_PORT = 8011
SECRET_KEY = os.urandom(24)
DEBUG = True
TCP_CLIENT_TIMEOUT = 5
