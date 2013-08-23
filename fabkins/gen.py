#!/usr/bin/env python
# -*- coding:utf_8 -*-

import os
import shutil
import sys

import clize

import fabkins


@clize.clize(alias={'output': ('o',)})
def conf(output="fabkins.ini"):
    """ Generate a default configuration file for fabkins. """
    from settings import write_config_file
    write_config_file(output)


@clize.clize
def static(dest="static"):
    """ Generate the static files directory used by fabkins. """
    static_dir = os.path.join(fabkins.__path__[0], 'static')
    shutil.copytree(static_dir, dest)


def conf_entry_point():
    clize.run(conf)

def static_entry_point():
    clize.run(static)
