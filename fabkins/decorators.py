#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import redirect, url_for, flash, session
from functools import wraps

import services
from settings import default_params


def need_correct_job_label(vue):
    @wraps(vue)
    def decorated(*args, **kwargs):
        job_label = ""
        try:
            job_label = kwargs['job_label']
            services.get_job(job_label)
        except:
            flash(u'The job "%s" does not exist' % job_label, 'alert')
            return redirect(url_for('index'))
        else:
            return vue(*args, **kwargs)
    return decorated

def need_correct_job_and_build_label(vue):
    @wraps(vue)
    def decorated(*args, **kwargs):
        try:
            job_label = kwargs['job_label']
            services.get_job(job_label)
        except:
            flash(u'The job "%s" does not exist' % job_label, 'alert')
            return redirect(url_for('index'))
        else:
            try:
                build_label = kwargs['build_label']
                services.get_build_of_job(job_label, build_label)
            except:
                flash(u'The build "%s" does not exist' % build_label, 'alert')
                return redirect(url_for('view_job', job_label=job_label))
            else:
                return vue(*args, **kwargs)
    return decorated

def need_root(vue):
    @wraps(vue)
    def decorated(*args, **kwargs):
        if session.get('pw') != default_params.PASSWORD:
            return redirect(url_for('login'))
        return vue(*args, **kwargs)
    return decorated
