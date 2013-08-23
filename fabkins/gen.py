#!/usr/bin/env python
# -*- coding:utf_8 -*-

import os
import shutil
import sys

import clize

import fabkins


@clize.clize(alias={'output': ('o',), 'password': ('p',)})
def conf(output="fabkins.ini", password="password"):
    """
        Generate a default configuration file for fabkins.

        output: the output file (will be overriden)

        password: the password used for log-in (in clear, will be sha256summed)

        You will have to edit the output file manually.
        However, this command is able to sha256sum your password so you don't have to do that manually. See "--password" option.

    """
    from settings import write_config_file
    import hashlib
    password = hashlib.sha256(password).hexdigest()
    write_config_file(output, password)


@clize.clize
def static(dest="static"):
    """
        Generate the static files directory used by fabkins.

        dest: the output directory (will be created)
    """
    static_dir = os.path.join(fabkins.__path__[0], 'static')
    shutil.copytree(static_dir, dest)


def conf_entry_point():
    clize.run(conf)

def static_entry_point():
    clize.run(static)
