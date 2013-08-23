#!/usr/bin/env python
# -*- coding:utf_8 -*-

import os
import shutil

import clize

import fabkins


@clize.clize
def conf(dest="fabkins.ini"):
    """ Generate a default configuration file for fabkins. """
    open(dest, "w")

@clize.clize
def static(dest="static"):
    """ Generate the static files directory used by fabkins. """
    static_dir = os.path.join(fabkins.__path__[0], 'static')
    shutil.copytree(static_dir, dest)


def conf_entry_point():
    import sys
    try:
       conf(*sys.argv)
    except clize.ArgumentError:
       conf(sys.argv[0], '-h')

def static_entry_point():
    import sys
    try:
        static(*sys.argv)
    except clize.ArgumentError:
        static(sys.argv[0], '-h')

