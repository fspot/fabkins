#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import datetime
import hashlib
from time import time

from flask import (Flask, render_template, jsonify,
    request, redirect, url_for, g, flash, session)

from decorators import (need_correct_job_label,
    need_correct_job_and_build_label, need_root)
from settings import default_params, get_default_fabfile_content
import services

PRE = default_params.WEB_PREFIX
app = Flask(__name__, static_url_path=PRE+'/static')
app.secret_key = default_params.SECRET_KEY
app.debug = default_params.DEBUG

# login

@app.route(PRE+'/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['pw'] = hashlib.sha256(request.form['pw']).hexdigest()
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route(PRE+'/logout')
def logout():
    session.pop('pw', None)
    return redirect(url_for('login'))

# views

@app.route(PRE+'/')
@need_root
def index():
    jobs = services.get_all_jobs().values()
    return render_template('jobs.html', jobs=jobs)

@app.route(PRE+'/job/<job_label>/')
@need_correct_job_label
@need_root
def view_job(job_label):
    try:
        job = services.get_job(job_label)
    except:
        flash(u'The job "%s" does not exist' % job_label, 'alert')
        return redirect(url_for('index'))
    done = services.get_builds_of_job(job_label, status="done") or None
    doing = services.get_builds_of_job(job_label, status="doing") or None
    todo = services.get_builds_of_job(job_label, status="todo") or None
    return render_template('job.html', **locals())

@app.route(PRE+'/job/<job_label>/', methods=['POST'])
@need_correct_job_label
@need_root
def delete_builds(job_label):
    builds = request.form.get("builds")
    if builds is not None:
        builds = builds.split(',')
        for build_label in builds:
            try:
                services.delete_build_of_job(job_label, build_label)
            except:
                flash(u'An error occured during build deletion', 'alert')
                break
        else:
            flash(u'%d builds were removed' % len(builds), 'success')
    return redirect(url_for('view_job', job_label=job_label))

@app.route(PRE+'/job/<job_label>/build/<build_label>/')
@need_correct_job_and_build_label
@need_root
def view_build(job_label, build_label):
    job = services.get_job(job_label)
    build = services.get_build_of_job(job_label, build_label)
    success = (build.status == "done" and build.code == "0")
    if build.status == "done":
        output = ''.join(build.output()).decode('utf8')
    return render_template('build.html', **locals())

@app.route(PRE+'/history/')
@need_root
def view_history():
    todo, doing, done = [], [], []
    for l in services.get_all_jobs().iterkeys():
        new_todo = [(l,b) for b in services.get_builds_of_job(l, "todo")]
        new_doing = [(l,b) for b in services.get_builds_of_job(l, "doing")]
        new_done = [(l,b) for b in services.get_builds_of_job(l, "done")]
        todo.extend(new_todo)
        doing.extend(new_doing)
        done.extend(new_done)
    todo.sort(key=lambda x:x[1].created_at, reverse=True)
    doing.sort(key=lambda x:x[1].start, reverse=True)
    done.sort(key=lambda x:x[1].start, reverse=True)
    return render_template('history.html', **locals())

# new/edit job

@app.route(PRE+'/job/new/')
@need_root
def new_job():
    return render_template('new_job.html', fabfile=get_default_fabfile_content(), edit=False)

@app.route(PRE+'/job/new/', methods=['POST'])
@need_root
def new_job_post():
    title = request.form.get('title')
    description = request.form.get('description')
    fabfile = request.form.get('fabfile')
    if None not in (title, description, fabfile):
        title = title.strip()
        description = description.strip()
        if title != '' and description != '':
            label = services.labelify(title)
            job = services.create_job(label, title, description, fabfile)
            flash(u'Job created', 'success')
            return redirect(url_for('view_job', job_label=job.label))
    # else : error !
    flash(u'Wrong data submited, try again', 'alert')
    if fabfile is None:
        fabfile = get_default_fabfile_content()
    return render_template('new_job.html', fabfile=fabfile)

@app.route(PRE+'/job/<job_label>/edit/')
@need_root
@need_correct_job_label
def edit_job(job_label):
    job = services.get_job(job_label)
    fabfile = ''.join(job.fabfile())
    return render_template('new_job.html', fabfile=fabfile, edit=True, job=job)

@app.route(PRE+'/job/<job_label>/edit/', methods=['POST'])
@need_root
@need_correct_job_label
def edit_job_post(job_label):
    job = services.get_job(job_label)
    fabfile = request.form.get('fabfile')
    if fabfile is None:
        flash(u'Wrong data submited, try again', 'alert')
        fabfile = ''.join(job.fabfile())
        return render_template('new_job.html', fabfile=fabfile, edit=True, job=job)
    services.edit_job(job_label, fabfile)
    flash(u'Job edited', 'success')
    return redirect(url_for('view_job', job_label=job.label))

# launch

@app.route(PRE+'/job/<job_label>/build/launch/')
@need_root
@need_correct_job_label
def prepare_build_job(job_label):
    job = services.get_job(job_label)
    fab_l = services.get_fab_l_of_job(job_label)
    return render_template('run_form.html', **locals())

@app.route(PRE+'/job/<job_label>/build/launch/', methods=['POST'])
@need_root
@need_correct_job_label
def build_job(job_label):
    fabfile = services.get_fabfile_path(job_label)
    args = request.form["args"]
    parallelize = (request.form["parallelize"] == u'on')
    cmd = 'fab -f "{0}" {1}'.format(fabfile, args)
    build = services.create_build(job_label, 'fab %s' % args)
    build.full_cmd = cmd
    doing = services.get_builds_of_job(job_label, status="doing")
    if parallelize or len(doing) == 0:
        pid = app.kmd.cmd(cmd)
        services.add_process(pid, build)
        return redirect(url_for('watch_build', job_label=job_label, build_label=build.label, pid=pid))
    flash(u'Build queued', 'success')
    return redirect(url_for('view_build', job_label=job_label, build_label=build.label))

# watch

@app.route(PRE+'/job/<job_label>/build/<build_label>/watch/<pid>')
@app.route(PRE+'/job/<job_label>/build/<build_label>/watch/')
@app.route(PRE+'/job/<job_label>/watch/')
@need_correct_job_label
@need_root
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
    job = services.get_job(job_label)
    build = services.get_build_of_job(job_label, build_label)
    return render_template('watch.html', **locals())

### ERRORS ###
##############

@app.errorhandler(500)
def ma_page_erreur(error):
    return render_template('500.html')


### WebHook ###
###############

@app.route(PRE+'/hook/<key>/<job_label>/', methods=['GET', 'POST'])
@app.route(PRE+'/hook/<key>/<job_label>/<before>/', methods=['GET', 'POST'])
@need_correct_job_label
def web_hook(key, job_label, before=None):
    if key != default_params.WEBHOOK_KEY:
        return jsonify({'response': 'wrong key'})
    parallelize = request.args.get('parallelize')
    if before is None:
        before = request.args.get('before') or ''
    data = ""
    if request.method == 'POST':
        data = request.json or dict(request.form.items())
        data = ":'{0}'".format(json.dumps(data).replace(',', '\,'))
    args = before + data
    fabfile = services.get_fabfile_path(job_label)
    cmd = 'fab -f "{0}" {1}'.format(fabfile, args)
    build = services.create_build(job_label, 'fab %s' % args)
    build.full_cmd = cmd
    doing = services.get_builds_of_job(job_label, status="doing")
    if parallelize or len(doing) == 0:
        pid = app.kmd.cmd(cmd)
        services.add_process(pid, build)
    return jsonify({'response': 'thx'})

### API ###
###########

@app.route(PRE+'/api/')
def api_index():
    return jsonify({'test': 'api works!'})

@app.route(PRE+'/api/job/')
def api_list_jobs():
    jobs = services.get_all_jobs()
    jobs = [{l: j.to_dict()} for (l, j) in jobs.iteritems()]
    return jsonify({'jobs': jobs})

@app.route(PRE+'/api/job/<job_label>/')
@need_correct_job_label
def api_view_job(job_label):
    job = services.get_job(job_label)
    return jsonify({job_label: job.to_dict()})

@app.route(PRE+'/api/job/<job_label>/build/')
@need_correct_job_label
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


### Before request ###
######################

@app.before_request
def before_request():
    g.request_start_time = time()
    g.request_time = lambda: "%.0f ms" % (1000.0*(time() - g.request_start_time))

