#!/usr/bin/env python
# -*- coding:utf-8 -*-

from os.path import join
import unicodedata
import shlex
import subprocess

from database import db
from settings import default_params


def get_all_jobs():
    return db.jobs

def get_job(job_label):
    return db.get_job(job_label)

def get_builds_of_job(job_label, status=None):
    if status is None:
        job = get_job(job_label)
        return job.builds
    else:
        builds = get_builds_of_job(job_label)
        builds = (b for b in builds.itervalues() if b.status == status)
        return sorted(builds, key=lambda x: x.created_at)

def get_build_of_job(job_label, build_label):
    return get_builds_of_job(job_label)[build_label]

def get_fabfile_path(job_label):
    return join(default_params.WORKDIR, 'jobs', job_label, 'fabfile.py')

def create_build(job_label, cmd):
    return db.create_build(job_label, cmd)

def create_job(job_label, title, description, fabfile):
    job = db.create_job(job_label, title, description)
    job.write_fabfile(fabfile.split('\n'))
    return job

def edit_job(job_label, fabfile):
    job = get_job(job_label)
    job.write_fabfile(fabfile.split('\n'))
    return job

def add_process(pid, build):
    db.add_process(int(pid), build)

def info_process(pid):
    return db.procs.get(int(pid))

def get_job_of_build(build):
    for job in get_all_jobs().itervalues():
        if build in job.builds.itervalues():
            return job

def close_process(pid, *args):
    build = db.close_process(int(pid), *args)
    job = get_job_of_build(build)
    todo = get_builds_of_job(job.label, status="todo")
    doing = get_builds_of_job(job.label, status="doing")
    if len(todo) > 0 and len(doing) == 0:
        next_build = todo[0]
        from flaskapp import app
        pid = app.kmd.cmd(next_build.full_cmd)
        add_process(pid, next_build)

def process_of_build(job_label, build_label):
    job = get_job(job_label)
    build = job.builds[build_label]
    return build.proc

def processing_builds_of_job(job_label):
    job = get_job(job_label)
    return [b for b in job.builds.itervalues() if b.status == "doing"]

def write_output(pid, lines):
    build = info_process(int(pid))
    build.write_output(lines)

def labelify(title):
    # title must be utf8 encoded
    s = title.strip().replace(' ', '_').lower()
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def delete_build_of_job(job_label, build_label):
    db.delete_build(job_label, build_label)

def get_fab_l_of_job(job_label):
    fabfile = get_fabfile_path(job_label)
    cmd = 'fab -f "%s" -l' % fabfile
    splitted = shlex.split(cmd)
    proc = subprocess.Popen(
        splitted,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return proc.stdout.read()
