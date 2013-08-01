#!/usr/bin/env python
# -*- coding:utf-8 -*-

### IMPORTS : stdlib ; libs ; mycode ###
########################################

import gevent
from gevent.server import StreamServer
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

import settings
from commander import Commander
from tcpsocket import LinesHandler
from websocket import handle_websocket


### Socket stuff ###
####################

sck = {}
lines_handler = LinesHandler(sck)


### WSGI app stuff ###
######################

from flaskapp import app

def my_app(environ, start_response):
    path = environ["PATH_INFO"]
    if path == "/":
        return app(environ, start_response)
    elif path == "/websocket":
        handle_websocket(environ["wsgi.websocket"], lines_handler)
    else:
        return app(environ, start_response)


### Commander stuff ###
#######################

app.kmd = Commander()
app.kmd.start()


### main ###
############

if __name__ == '__main__':
    http_server = WSGIServer(('', settings.WEB_PORT), my_app, handler_class=WebSocketHandler)
    http_server.start()
    tcp_server = StreamServer(('', settings.TCP_PORT), lines_handler.handle)
    try:
        tcp_server.serve_forever()
    except:
        pass
    app.kmd.stop()
