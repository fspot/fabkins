#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import datetime
from time import time

from flask import Flask, render_template, jsonify, request, redirect

import settings
import services

app = Flask(__name__)
app.secret_key = settings.SECRET_KEY
app.debug = settings.DEBUG


@app.route('/')
def index():
    jobs = services.get_all_jobs().values()
    return render_template('jobs.html', jobs=jobs)

@app.route('/job/<job_label>/')
def view_job(job_label):
    job = services.get_job(job_label)
    doing = [b for b in job.builds.itervalues() if b.status == "doing"] or None
    done = [b for b in job.builds.itervalues() if b.status == "done"] or None
    return render_template('job.html', job=job, doing=doing, done=done)

@app.route('/cmd/<path:cmd>')
def launch_cmd(cmd):
    return "<pre>{0} ==> {1}</pre>".format(cmd, repr(app.kmd.cmd(cmd)))

@app.route('/watch')
@app.route('/watch/<job_label>/<build_label>/<pid>/')
def websocket_page(job_label=None, build_label=None, pid=None):
    if pid is not None:
        job = services.get_job(job_label)
        build = job.builds[build_label]
    return render_template('watch.html', **locals())

@app.route('/job/<job_label>/build/launch/')
def prepare_build_job(job_label):
    job = services.get_job(job_label)
    return render_template('run_form.html', job=job)

@app.route('/job/<job_label>/build/<build_label>/watch/<pid>')
@app.route('/job/<job_label>/build/<build_label>/watch/')
@app.route('/job/<job_label>/watch/')
def watch_build(job_label, build_label=None, pid=None):
    if pid is None and build_label is not None:
        pid = services.process_of_build(job_label, build_label) or '0'
    elif build_label is None:
        builds = services.processing_builds_of_job(job_label)
        if not builds:
            pid = '0'
            job_label = '0'
        else:
            pid = builds[0].proc
            build_label = builds[0].label
    return redirect('/watch/{1}/{2}/{0}/#{0};{1};{2}'.format(pid, job_label, build_label))

@app.route('/job/<job_label>/build/launch/', methods=['POST'])
def build_job(job_label):
    fabfile = services.get_fabfile_path(job_label)
    cmd = "fab -f {0} {1}".format(
        fabfile,
        request.form["args"]
    )
    build = services.create_build(job_label, cmd)
    pid = app.kmd.cmd(cmd)
    services.add_process(pid, build)
    return redirect('/watch/{1}/{2}/{0}/#{0};{1};{2}'.format(pid, job_label, build.label))


### API ###
###########

@app.route('/api/')
def api_index():
    return jsonify({'test': 'api works!'})

@app.route('/api/job/')
def api_list_jobs():
    jobs = services.get_all_jobs()
    jobs = [{l: j.to_dict()} for (l, j) in jobs.iteritems()]
    return jsonify({'jobs': jobs})

@app.route('/api/job/<job_label>/')
def api_view_job(job_label):
    job = services.get_job(job_label)
    return jsonify({job_label: job.to_dict()})

@app.route('/api/job/<job_label>/build/')
def api_builds_of_job(job_label):
    builds = services.get_builds_of_job(job_label)
    builds = [{bl: b.to_dict()} for bl, b in builds.iteritems()]
    return jsonify({'builds': builds})



### JINJA ###
#############

@app.template_filter('strftime')
def _jinja2_filter_timestamp(ts, fmt):
    date = datetime.datetime.fromtimestamp(ts)
    return date.strftime(fmt)

@app.template_filter('filtattrval')
def _jinja2_filter_filtattrval(elems, attr, value, inverse=False):
    def takeit(e, a, b):
        try:
            a = getattr(e, a)
            if inverse:
                return a != b
            else:
                return a == b
        except:
            return False
    return [e for e in elems if takeit(e, attr, value)]

@app.template_filter('duration')
def _jinja2_filter_duration(duration):
    duration = int(duration)
    output = ''
    h, duration = duration / 3600, duration % 3600
    m, s = duration / 60, duration % 60
    if h > 0: output += '%dh' % h
    if m > 0: output += '%dm' % m
    output += '%ds' % s
    return output

@app.context_processor
def passer_aux_templates():
    return dict(gettime=time)
