#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import json


class LinesHandler(object):
    def __init__(self, sck):
        self.sck = sck
        self.outputs = {}

    def dispatch(self, msg):
        for name, ws in self.sck.iteritems():
            if ws.handler.subscribe == msg['pid']:
                print "sending %s to %s" % (repr(msg), name)
                ws.send(json.dumps(msg))

    def handle(self, sock, address):
        print '<tcp client %s:%s>' % address
        fileobj = sock.makefile()
        while True:
            line = fileobj.readline().decode("utf-8")
            if not line:
                print '<tcp client disconnected>'
                break
            if line.strip().lower() == 'quit':
                print '<tcp client quit>'
                break
            first_part, line = line.split(' ', 1)
            if 'FABKINS' in first_part:
                pid, line = line.split(' ', 1)
                msg = {
                    'type': first_part,
                    'pid': pid,
                    'line': line
                }
                if 'BEGIN' in first_part:
                    self.outputs[pid] = []
                elif 'END' in first_part:
                    import services
                    services.write_output(pid, self.outputs[pid])
                    del self.outputs[pid]
                    services.close_process(pid, line)
            else:
                msg = {
                    'type': 'line',
                    'pid': first_part,
                    'line': line
                }
                self.outputs[msg['pid']].append(line)
            self.dispatch(msg)

