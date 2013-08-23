#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
from os.path import join

import clize


def patch_fabric_local_flush():
	import fabric
	opfile = join(fabric.__path__[0], "operations.py")
	fd = open(opfile, 'r')
	lines = fd.readlines()
	fd.close()

	def patch_line(l):
		if l.endswith('print("[localhost] local: " + given_command)\n')\
		   and not "FABKINS_PATCH" in l:
			return l.rstrip('\n') + "; sys.stdout.flush()  # FABKINS_PATCH\n"
		return l

	lines = [patch_line(l) for l in lines]

	fd = open(opfile, 'w')
	fd.writelines(lines)
	fd.close()

@clize.clize
def main():
	""" This tool lets you patch your fabkins virtualenv. """
	try:
		# check we are in a virtualenv:
		if hasattr(sys, 'real_prefix'):
			# check this is (probably) the fabkins virtualenv
			import fabric, gevent, flask
			# ok, we can patch :
			patch_fabric_local_flush()
			print 'Done !'
	except:
		print "This tool lets you patch your fabkins virtualenv."
		print "Usage : python patch.py"

def main_entry_point():
	clize.run(main)


if __name__ == '__main__':
	main_entry_point()
