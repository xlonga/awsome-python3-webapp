#!/usr/bin/env pyhton3
# -*- coding: utf-8 -*-

__author__ = 'xlonga Huang'

import os, sys, time, subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def log(s):
	print('[Monitor]%s' % s)

class MyFileSystemEventHandler(FileSystemEventHandler):
	
	def __init__(self, fn):
		super(MyFileSystemEventHandler, self).__init__()
		self.restart = fn

	def on_any_event(self, event):
		if event.src_path.endswith('.py'):
			log('Python source file changed: %s' % event.src_path)
			self.restart()

command = ['echo', 'ok']
process = None

def kill_process():
	global process
	if process:
		log('Kill process [%s]...' % process.pid)
		process.kill()
		process.wait()
		log('Process ended with code %s.' % process.returncode)
		process = None

def start_process():
	global process, command
	log('Start process %s...' % ' '.join(command))
	process = subprocess.Popen(command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

def restart_process():
	kill_process()
	start_process()

def start_watch(path, callback):
	observer = Observer()
	observer.schedule(MyFileSystemEventHandler(restart_process), path, recursive=True)
	observer.start()
	log('Wacthing directory %s...' % path)
	start_process()
	try:
		while True:
			time.sleep(0.8)
	except KeyboardInterrupt:
		observer.stop()
	observer.join()

if __name__ == '__main__':
	argv = sys.argv[1:]
	print('argv: ', argv)
	if not argv:
		print('Usage: ./pymonitor your-script.py')
		exit(0)
	if argv[0] != 'python3':
		argv.insert(0, 'python3')
	command = argv
	path = os.path.abspath('.')
	start_watch(path, None)