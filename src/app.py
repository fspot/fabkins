#!/usr/bin/env python
# -*- coding:utf-8 -*-

from gevent.server import StreamServer
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import clize

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


### main ###
############

@clize.clize
def main():
    """ Fabkins, a femto-jenkins based on fabfiles. """
    app.kmd = Commander()
    app.kmd.start()
    http_server = WSGIServer(('', settings.WEB_PORT), my_app, handler_class=WebSocketHandler)
    http_server.start()
    tcp_server = StreamServer(('', settings.TCP_PORT), lines_handler.handle)
    try:
        tcp_server.serve_forever()
    except:
        pass
    app.kmd.stop()

def main_entry_point():
    """ this function is an entry_point for main() """
    import sys
    try:
       main(*sys.argv)
    except clize.ArgumentError:
       main(sys.argv[0], '-h')

if __name__ == '__main__':
    main_entry_point()

