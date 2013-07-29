#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from os.path import join
import json
import datetime
from time import time

import settings
from models import Job, Build


class Database(object):
    def __init__(self):
        self.refresh_jobs()
        self.procs = {}

    def create_job(self, job_label, job_title, description, template=None):
        job_dir = join(settings.WORKDIR, 'jobs', job_label)
        os.mkdir(job_dir)
        os.mkdir(join(job_dir, 'builds'))
        f = open(join(job_dir, 'config.json'), 'w')
        job_infos = {
            "title": job_title,
            "label": job_label,
            "description": description,
            "created_at": time(),
            "version": 1,
        }
        f.write(json.dumps(job_infos, indent=2))
        f.close()
        j = Job(job_dir, self)
        self.jobs[j.label] = j
        return j

    def refresh_jobs(self):
        self.jobs_dir = join(settings.WORKDIR, 'jobs')
        labels = os.listdir(self.jobs_dir)
        self.jobs = {}
        for label in labels:
            job_dir = join(self.jobs_dir, label)
            self.jobs[label] = Job(job_dir, self)

    def get_job(self, label):
        return self.jobs[label]

    def get_builds(self, job_label, j=None):
        if j is None:
            j = self.get_job(job_label)
        builds_dir = join(settings.WORKDIR, 'jobs', job_label, 'builds')
        return dict((d, Build(j, join(builds_dir, d))) for d in os.listdir(builds_dir))

    def create_build(self, job_label, cmd):
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        build_dir = join(settings.WORKDIR, 'jobs', job_label, 'builds', date)
        os.mkdir(build_dir)
        f = open(join(build_dir, 'build_info.json'), 'w')
        build_infos = {
            "cmd": cmd,
            "label": date,
            "start": time(),
        }
        f.write(json.dumps(build_infos, indent=2))
        f.close()
        j = self.get_job(job_label)
        b = Build(j, build_dir, "todo")
        j.builds[date] = b
        return b

    def add_process(self, pid, build):
        build.proc = pid
        build.status = "doing"
        self.procs[pid] = build

    def close_process(self, pid, *args):
        build = self.procs[pid]
        build.status = "done"
        build.proc = None
        build.json['end'] = time()
        build.json['code'] = args[0].strip()
        build.save()
        del self.procs[pid]

db = Database()
