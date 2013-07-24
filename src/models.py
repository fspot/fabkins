#!/usr/bin/env python
# -*- coding:utf-8 -*-

from os.path import join, basename
import json


class Job(object):
    def __init__(self, job_json, db):
        self.json = job_json
        self.db = db
        self.builds = self.db.get_builds(self.json["label"])

    def create_build(self, cmd):
        return self.db.create_build(self.json["label"], cmd)


class Build(object):
    def __init__(self, build_dir, status="done"):
        self.dir = build_dir
        self.label = basename(build_dir)
        self.json = json.loads(open(join(self.dir, 'build_info.json')).read())
        self.status = status
        self.proc = None

    def output(self):
        return open(join(self.dir, 'output.txt')).read()

    def write_output(self, lines):
        f = open(join(self.dir, 'output.txt'), 'w')
        f.writelines(lines)
        f.close()

    def to_dict(self):
        copy = self.json.copy()
        copy.update({
            'status': self.status,
            'label': self.label,
            'proc': self.proc
        })
        return copy

    def save(self):
        f = open(join(self.dir, 'build_info.json'), 'w')
        f.write(json.dumps(self.to_dict(), indent=2))
        f.close()

class Process(object):
    def __init__(self):
        pass
