#!/usr/bin/env python
# -*- coding:utf-8 -*-

### IMPORTS : stdlib ; libs ; mycode ###
########################################

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

from flaskapp import app

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

app.kmd = Commander()
app.kmd.start()


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
    app.kmd.stop()
