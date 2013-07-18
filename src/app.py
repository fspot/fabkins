#!/usr/bin/env python
# -*- coding:utf-8 -*-

### IMPORTS : stdlib ; libs ; mycode ###
########################################

import os

from flask import Flask, render_template
from gevent.server import StreamServer
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from commander import Commander
from tcpsocket import LinesHandler
from websocket import handle_websocket


### SOCKETS stuff ###
#####################

sck = {}


### WSGI APP stuff ###
######################

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True

def my_app(environ, start_response):
    path = environ["PATH_INFO"]
    if path == "/":
        return app(environ, start_response)
    elif path == "/websocket":
        handle_websocket(environ["wsgi.websocket"], sck)
    else:
        return app(environ, start_response)


### COMMANDER stuff ###
#######################

kmd = Commander()
kmd.start()


### Flask views ###
###################

@app.route('/')
def index():
    """ Racine """
    return "<pre>it works !</pre>"

@app.route('/cmd/<path:cmd>')
def launch_cmd(cmd):
    return "<pre>{0} ==> {1}</pre>".format(cmd, repr(kmd.cmd(cmd, True)))

@app.route('/ws')
def websocket_page():
    return render_template('index.html')


### MAIN ###
############

if __name__ == '__main__':
    http_server = WSGIServer(('', 8010), my_app, handler_class=WebSocketHandler)
    http_server.start()
    lines_handler = LinesHandler(sck)
    tcp_server = StreamServer(('', 8011), lines_handler.handle)
    try:
        tcp_server.serve_forever()
    except KeyboardInterrupt:
        pass
    kmd.stop()