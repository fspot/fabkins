#!/usr/bin/env python
# -*- coding:utf-8 -*-

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

    logging.info("<sender up!>")
    while True:
        out = outputs.get()
        line = ' '.join(out)
        print "::: to ze internets :", line.rstrip("\n")
        sk.sendall(line.rstrip("\n") + '\n')
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


def run_command(cmd, outputs=None):
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

    logging.info("<WORKER: CMD %s END !>" % cmd)
    return proc.poll()
