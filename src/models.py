#!/usr/bin/env python
# -*- coding:utf-8 -*-

from os.path import join, basename
import json


class Job(object):
    def __init__(self, job_dir, db):
        self.dir = job_dir
        self.db = db
        self.reload()
        self.builds = self.db.get_builds(self.label, self)

    def fabfile(self):
        return open(join(self.dir, 'fabfile.py')).readlines()

    def write_fabfile(self, lines):
        f = open(join(self.dir, 'fabfile.py'), 'w')
        f.writelines(lines)
        f.close()

    def create_build(self, cmd):
        return self.db.create_build(self.label, cmd)

    def reload(self):
        self.json = json.loads(open(join(self.dir, 'config.json')).read())

    def save(self):
        f = open(join(self.dir, 'config.json'), 'w')
        f.write(json.dumps(self.to_dict(), indent=2))
        f.close()

    def to_dict(self, with_builds=False):
        copy = self.json.copy()
        if with_builds:
            copy.update({'builds': self.builds.to_dict()})
        return copy

    def __getattr__(self, attr):
        return self.json[attr]


class Build(object):
    def __init__(self, job, build_dir, status=None):
        self.dir = build_dir
        self.label = basename(build_dir)
        self.proc = None
        self.job = job
        if status is not None:
            self.status = status
        self.reload()

    def output(self):
        return open(join(self.dir, 'output.txt')).readlines()

    def write_output(self, lines):
        f = open(join(self.dir, 'output.txt'), 'w')
        f.writelines(lines)
        f.close()

    def reload(self):
        self.json = json.loads(open(join(self.dir, 'build_info.json')).read())

    def save(self):
        f = open(join(self.dir, 'build_info.json'), 'w')
        f.write(json.dumps(self.to_dict(), indent=2))
        f.close()

    def to_dict(self, with_job=False):
        copy = self.json.copy()
	if hasattr(self, 'start'):
            copy.update({'start': self.start})
        copy.update({
            'status': self.status,
            'label': self.label,
            'proc': self.proc
        })
        if with_job:
            copy.update({'job': self.job.to_dict()})
        return copy

    def __getattr__(self, attr):
        return self.json[attr]


class Process(object):
    def __init__(self):
        pass
