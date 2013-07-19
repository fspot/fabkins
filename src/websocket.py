#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json


def handle_start(ws, msg, sck):
    ws.subscribe = msg['subscribe']
    ws.state = 'subscribed'
    sck[ws.label] = ws
    # send begin build data here


def handle_msg(ws, msg):
    #ws.send(json.dumps({'output': r}))
    pass


def handle(ws, msg, sck):
    # load msg, check type TODO
    msg = json.loads(msg)
    if ws.state == 'start':
        handle_start(ws, msg, sck)
    else:
        handle_msg(ws, msg)


def handle_websocket(ws, sck):
    ws.label = '{0}:{1}'.format(*ws.socket.getpeername())
    ws.state = 'start'
    print "<WSS : BEGIN OF %s>" % ws.label
    
    while True:
	try:
            msg = ws.receive()
        except:
	    break
        if msg is None:
	    break
        else:
            handle(ws, msg, sck)
    
    # client quit
    if ws.label in sck:
        del sck[ws.label]
    print "<WSS : END OF %s>" % ws.label
