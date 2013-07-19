#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

from flask import Flask, render_template


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True


@app.route('/')
def index():
    """ Racine """
    return "<pre>it works !</pre>"

@app.route('/cmd/<path:cmd>')
def launch_cmd(cmd):
    return "<pre>{0} ==> {1}</pre>".format(cmd, repr(app.kmd.cmd(cmd, True)))

@app.route('/ws')
def websocket_page():
    return render_template('index.html')
