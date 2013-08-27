#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json


def handle_start(ws, msg, lines_handler):
    import services
    ws.subscribe = msg['subscribe']
    info = services.info_process(ws.subscribe)
    if info is None:
        ws.send(json.dumps({'type': 'NO_PROCESS'}))
        raise Exception("NO_PROCESS")
    print 'WSS : subscription to', ws.subscribe
    ws.state = 'subscribed'
    lines_handler.sck[ws.label] = ws
    # send begin build data here
    for line in lines_handler.outputs[ws.subscribe]:
        ws.send(json.dumps({
            'type': 'line',
            'pid': ws.subscribe,
            'line': line
        }))


def handle_msg(ws, msg):
    #ws.send(json.dumps({'output': r}))
    pass


def handle(ws, msg, lines_handler):
    # load msg, check type TODO
    msg = json.loads(msg)
    if ws.state == 'start':
        handle_start(ws, msg, lines_handler)
    else:
        handle_msg(ws, msg)


def handle_websocket(ws, lines_handler):
    ws.label = '{0}:{1}'.format(*ws.socket.getpeername())
    ws.state = 'start'
    ws.subscribe = None
    print "<WSS : BEGIN OF %s>" % ws.label

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
    if ws.label in lines_handler.sck:
        del lines_handler.sck[ws.label]
    print "<WSS : END OF %s>" % ws.label
