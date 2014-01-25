#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from multiprocessing import Process, Queue


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
    import time
    import logging
    from gevent import socket
    import settings

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s - %(message)s",
        datefmt='%d/%m/%Y %H:%M:%S',
        filename="sender.log"
    )

    sk = socket.socket()
    count = settings.TCP_CLIENT_TIMEOUT
    while count > 0:
        try:
            sk.connect(('localhost', settings.TCP_PORT))
            break
        except:
            time.sleep(0.1)
            count -= 0.1
    if count <= 0:
        logging.warn("/!\ Could not connect to tcp server /!\\")
        return

    def to_unicode(that):
        if isinstance(that, int): # return code or pid
            return unicode(that)
        elif isinstance(that, unicode):
            return that
        elif isinstance(that, str): # raw output string, should be utf-8
            return that.decode("utf-8")
        raise TypeError("wasn't supposed to unicodize type %s" % repr(type(that)))

    logging.info("<sender up!>")
    while True:
        try:
            out = outputs.get()
        except:
            break
        line = ' '.join(to_unicode(e) for e in out)
        line = line.rstrip("\n") + "\n" # be sure there's 1 trailing \n
        print "::: to ze internets :", line.encode("utf-8"), # again utf-8 :)
        sk.sendall(line.encode("utf-8"))
    logging.info("<sender down!>")


def master(queue, rep_queue, outputs):
    from multiprocessing import Process
    import logging
    from settings import add_fab_to_env_path

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        filename="master.log"
    )

    logging.info("<master up!>")
    add_fab_to_env_path()
    workers = []
    while True:
        try:
            (cmd,) = queue.get()
        except:
            break
        logging.debug("master rcv cmd : %s" % cmd)
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
    logging.info("<master down!>")


def run_command(cmd, outputs):
    from multiprocessing import current_process
    import subprocess
    import shlex
    import logging

    if cmd.strip() == '':
        logging.info("<WORKER: CMD VOID>")
        return
    logging.info("<WORKER: CMD %s START>" % cmd)
    try:
        splitted = shlex.split(cmd)
        proc = subprocess.Popen(
            splitted,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except OSError:
        logging.info("<WORKER: CMD %s WRONG>" % repr(splitted))
        return

    outputs.put(['<FABKINS_BEGIN>', current_process().pid, cmd])

    line = str() # yep, no unicode, because 'out' can be e.g. '\xc3'
    while True:
        out = proc.stdout.read(1)
        if out == '' and proc.poll() is not None:
            break
        if out != '':
            line += out
            if out == '\n':
                outputs.put([current_process().pid, line])
                line = str()

    outputs.put(['<FABKINS_END>', current_process().pid, proc.poll()])

    logging.info("<WORKER: CMD %s END !>" % cmd)
    return proc.poll()
