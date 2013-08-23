#!/usr/bin/env python
# -*- coding:utf_8 -*-

import clize


@clize.clize
def conf():
    pass

@clize.clize
def static():
    pass


def conf_entry_point():
    conf()

def static_entry_point():
    static()

