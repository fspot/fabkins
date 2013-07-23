#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from os.path import join

from database import db
import settings


def get_all_jobs():
    return db.jobs

def get_job(job_label):
    return db.get_job(job_label)

def get_builds_of_job(job_label):
    job = get_job(job_label)
    return job.builds

def get_fabfile_path(job_label):
    return join(settings.WORKDIR, 'jobs', job_label, 'fabfile.py')

def create_build(job_label, cmd):
    return db.create_build(job_label, cmd)

def add_process(pid, build):
    db.add_process(int(pid), build)

def info_process(pid):
    return db.procs.get(int(pid))

def close_process(pid):
    db.close_process(int(pid))

def write_output(pid, lines):
    build = info_process(int(pid))
    build.write_output(lines)
