#!/usr/bin/env python
# -*- coding:utf-8 -*-

from gevent.server import StreamServer
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import clize

from settings import default_params, read_config_file, TCP_PORT, add_fab_to_env_path
from commander import Commander
from tcpsocket import LinesHandler
from websocket import handle_websocket


@clize.clize(alias={'config_file': ('c',)})
def main(config_file="<path>", fabfile="<path>", workdir="<path>",
         web_port=default_params.WEB_PORT, web_prefix="<str>", password="<str>",
         webhook_key="<str>", secret_key="<str>", debug="<str>"):
    """
        Fabkins, a femto-jenkins based on fabfiles.

        config_file: path of fabkins.ini

        fabfile: path of default fabfile.py template

        workdir: path of fabkins working directory

        web_port: listening http port

        web_prefix: '/fabkins' if your instance is at example.com/fabkins

        password: the password used for log-in (sha256sum)

        webhook_key: the password used to trigger web hooks

        ProTip /!\ you should probably just use the "-c" option.
        First, generate a "fabkins.ini" file -> "fabkins-gen-config -o ./fabkins.ini"
        Edit it, and then launch fabkins -> "fabkins -c ./fabkins.ini"
    """

    ### Config stuff

    add_fab_to_env_path()
    if config_file != "<path>": read_config_file(config_file)

    if fabfile != "<path>":     default_params.DEFAULT_FABFILE = fabfile
    if workdir != "<path>":     default_params.WORKDIR = workdir
    if web_port != default_params.WEB_PORT: default_params.WEB_PORT = int(web_port)
    if web_prefix != "<str>":  default_params.WEB_PREFIX = web_prefix
    if password != "<str>":    default_params.PASSWORD = password
    if webhook_key != "<str>": default_params.WEBHOOK_KEY = webhook_key
    if secret_key != "<str>":  default_params.SECRET_KEY = secret_key
    if debug != "<str>":       default_params.DEBUG = (debug=="yes")

    print "Conf :"
    print "   fabfile: ", default_params.DEFAULT_FABFILE
    print "   workdir: ", default_params.WORKDIR
    print "   webport: ", default_params.WEB_PORT
    print "   webpref: ", default_params.WEB_PREFIX
    print "   passwrd: ", default_params.PASSWORD
    print "   webhook: ", default_params.WEBHOOK_KEY
    print "   debugmd: ", default_params.DEBUG

    ### Socket stuff

    sck = {}
    lines_handler = LinesHandler(sck)


    ### WSGI app stuff

    from flaskapp import app

    def my_app(environ, start_response):
        path = environ["PATH_INFO"]
        if path == "/":
            return app(environ, start_response)
        elif path == "/websocket":
            handle_websocket(environ["wsgi.websocket"], lines_handler)
        else:
            return app(environ, start_response)


    ### Start all

    app.kmd = Commander()
    app.kmd.start()
    http_server = WSGIServer(('', default_params.WEB_PORT), my_app, handler_class=WebSocketHandler)
    http_server.start()
    tcp_server = StreamServer(('', TCP_PORT), lines_handler.handle)
    try:
        tcp_server.serve_forever()
    except:
        pass
    app.kmd.stop()


def main_entry_point():
    """ this function is an entry_point for main() """
    clize.run(main)


if __name__ == '__main__':
    main_entry_point()
