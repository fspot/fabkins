#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
from multiprocessing import Process, Queue, current_process

from gevent import socket

import settings


class Commander(object):
    def __init__(self):
        self.queue = Queue()
        self.rep_queue = Queue()
        self.outputs = Queue()
        self.master = Process(target=master, args=[self.queue, self.rep_queue, self.outputs])
        self.sender = Process(target=sender, args=[self.outputs])

    def start(self):
        self.master.start()
        self.sender.start()

    def stop(self):
        self.sender.terminate()
        self.master.terminate()

    def cmd(self, c):
        self.queue.put((c,))
        return self.rep_queue.get()

    def list_cmd(self):
        return self.cmd("l")


def sender(outputs):
    sk = socket.socket()
    count = settings.TCP_CLIENT_TIMEOUT
    while count > 0:
        try:
            sk.connect(('localhost', settings.TCP_PORT))
            break
        except:
            time.sleep(0.1)
            count -= 1
    if count <= 0:
        print "/!\ Could not connect to tcp server /!\\"
        return

    print "<sender up!>"
    while True:
        out = outputs.get()
        line = ' '.join(out)
        print "::: to ze internets :", line.rstrip("\n")
        sk.sendall(line.rstrip("\n") + '\n')
    print "<sender down!>"


def master(queue, rep_queue, outputs):
    print "<master up!>"
    workers = []
    while True:
        try:
            (cmd,) = queue.get()
        except:
            break
        workers = [w for w in workers if w.is_alive()]  # gc ?
        if cmd == "l":
            rep = [(w.pid, w.cmd) for w in workers]
        else:
            w = Process(target=run_command, args=[cmd, outputs])
            w.cmd = cmd
            w.start()
            workers.append(w)
            rep = w.pid
        rep_queue.put(rep)
    print "<master down!>"


def run_command(cmd, outputs=None):
    import subprocess
    import shlex

    if cmd.strip() == '':
        print "<WORKER: CMD VOID>"
        return
    print "<WORKER: CMD %s START>" % cmd
    try:
        splitted = shlex.split(cmd)
        proc = subprocess.Popen(
            splitted,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except OSError:
        print "<WORKER: CMD %s WRONG>"
        return

    outputs.put(['<FABKINS_BEGIN>', str(current_process().pid), cmd])

    line = ''
    while True:
        out = proc.stdout.read(1)
        if out == '' and proc.poll() is not None:
            break
        if out != '':
            line += out
            if out == '\n':
                outputs.put([str(current_process().pid), line])
                line = ''

    outputs.put(['<FABKINS_END>', str(current_process().pid), str(proc.poll())])

    print "<WORKER: CMD %s END !>" % cmd
    return proc.poll()
