#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import json


def handle_start(ws, msg, lines_handler):
    import services
    ws.handler.subscribe = msg['subscribe']
    info = services.info_process(ws.handler.subscribe)
    if info is None:
        ws.send(json.dumps({'type': 'NO_PROCESS'}))
        print "WSS : woops, already finished !"
        ws.close()
        return
    print 'WSS : subscription to', ws.handler.subscribe
    ws.handler.state = 'subscribed'
    lines_handler.sck[ws.handler.label] = ws
    # send begin build data here
    for line in lines_handler.outputs[ws.handler.subscribe]:
        ws.send(json.dumps({
            'type': 'line',
            'pid': ws.handler.subscribe,
            'line': line
        }))


def handle_msg(ws, msg):
    #ws.send(json.dumps({'output': r}))
    pass


def handle(ws, msg, lines_handler):
    # load msg, check type TODO
    msg = json.loads(msg)
    if ws.handler.state == 'start':
        handle_start(ws, msg, lines_handler)
    else:
        handle_msg(ws, msg)


def handle_websocket(ws, lines_handler):
    ws.handler.label = '{0}:{1}'.format(*ws.handler.socket.getpeername())
    ws.handler.state = 'start'
    ws.handler.subscribe = None
    print "<WSS : BEGIN OF %s>" % ws.handler.label

    while True:
        try:
            msg = ws.receive()
        except:
            break
        if msg is None:
            break
        else:
            handle(ws, msg, lines_handler)

    # client quit
    if ws.handler.label in lines_handler.sck:
        del lines_handler.sck[ws.handler.label]
    print "<WSS : END OF %s>" % ws.handler.label
