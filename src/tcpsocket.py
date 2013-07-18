#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json


class LinesHandler(object):
    def __init__(self, sck):
        self.sck = sck

    def handle(self, sock, address):
        print '<tcp client %s:%s>' % address
        fileobj = sock.makefile()
        while True:
            line = fileobj.readline()
            if not line:
                print '<tcp client disconnected>'
                break
            if line.strip().lower() == 'quit':
                print '<tcp client quit>'
                break
            # fileobj.write('you said ' + line); fileobj.flush()
            for name,ws in self.sck.items():
                print "sending %s to %s" % (line, name)
                ws.send(json.dumps({'output': line}))
