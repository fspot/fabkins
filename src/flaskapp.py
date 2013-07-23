#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Flask, render_template, jsonify, request, redirect

import os
import settings
import services

app = Flask(__name__)
app.secret_key = settings.SECRET_KEY
app.debug = settings.DEBUG


@app.route('/')
def index():
    return "<pre>it works !</pre>"

@app.route('/cmd/<path:cmd>')
def launch_cmd(cmd):
    return "<pre>{0} ==> {1}</pre>".format(cmd, repr(app.kmd.cmd(cmd)))

@app.route('/ws')
def websocket_page():
    return render_template('index.html')

@app.route('/job/<job_label>/build/run/')
def prepare_build_job(job_label):
    return render_template('run_form.html', job_label=job_label)

### API ###
###########

@app.route('/api/')
def api_index():
    return jsonify({'test': 'api works!'})

@app.route('/api/job/')
def list_jobs():
    jobs = services.get_all_jobs()
    jobs = [{l: j.json} for (l, j) in jobs.iteritems()]
    return jsonify({'jobs': jobs})

@app.route('/api/job/<job_label>/')
def view_job(job_label):
    job = services.get_job(job_label)
    return jsonify({job_label: job.json})

@app.route('/api/job/<job_label>/build/')
def builds_of_job(job_label):
    builds = services.get_builds_of_job(job_label)
    builds = [{b.label: b.json} for b in builds]
    return jsonify({'builds': builds})

@app.route('/job/<job_label>/build/run/', methods=['POST'])
def build_job(job_label):
    fabfile = services.get_fabfile_path(job_label)
    cmd = "fab -f {0} {1}".format(
        fabfile,
        request.form["args"]
    )
    build = services.create_build(job_label, cmd)
    pid = app.kmd.cmd(cmd)
    services.add_process(pid, build)
    # return jsonify({'build': build.to_dict()})
    # {
    #   "build": {
    #     "cmd": "fab -f /home/fred/fabkinsdir/jobs/first_job/fabfile.py -l",
    #     "label": "2013-07-23_20-32-04",
    #     "proc": 21302,
    #     "status": "doing"
    #   }
    # }
    return redirect('/ws#%d' % pid)
