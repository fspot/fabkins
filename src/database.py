#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from os.path import join
import json
import datetime

import settings
from models import Job, Build


class Database(object):
    def __init__(self):
        self.refresh_jobs()
        self.procs = {}

    def refresh_jobs(self):
        self.jobs_dir = join(settings.WORKDIR, 'jobs')
        labels = os.listdir(self.jobs_dir)
        self.jobs = {}
        for label in labels:
            job_config = join(self.jobs_dir, label, "config.json")
            job = json.loads(open(job_config).read())
            self.jobs[label] = Job(job, self)

    def get_job(self, label):
        return self.jobs[label]

    def get_builds(self, job_label):
        builds_dir = join(settings.WORKDIR, 'jobs', job_label, 'builds')
        return dict((d, Build(join(builds_dir, d))) for d in os.listdir(builds_dir))

    def create_build(self, job_label, cmd):
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        build_dir = join(settings.WORKDIR, 'jobs', job_label, 'builds', date)
        os.mkdir(build_dir)
        f = open(join(build_dir, 'build_info.json'), 'w')
        f.write(json.dumps({"cmd": cmd}, indent=2))
        f.close()
        b = Build(build_dir, "todo")
        j = self.get_job(job_label)
        j.builds[date] = b
        return b

    def add_process(self, pid, build):
        build.proc = pid
        build.status = "doing"
        self.procs[pid] = build

    def close_process(self, pid):
        self.procs[pid].status = "done"
        self.procs[pid].proc = None
        del self.procs[pid]

db = Database()
