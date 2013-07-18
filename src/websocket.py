#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json


def handle_websocket(ws, sck):
    ws.label = '{0}:{1}'.format(*ws.socket.getpeername())
    sck[ws.label] = ws
    print "<WSS : BEGIN OF %s>" % ws.label
    while True:
        message = ws.receive()
        if message is None:
            break
        else:
            r  = "I have received : %s" % repr(message)
            ws.send(json.dumps({'output': r}))
    del sck[ws.label]
    print "<WSS : END OF %s>" % ws.label