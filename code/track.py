#!/usr/bin/env python

import sys
import os
import json
import datetime

path = os.getenv("HOME")

# Internal

def load():
	f = open(path + '/.timetracker/data.json', 'r')
	x = f.read()
	f.close()
	return json.loads(x)


def save(x):
	f = open(path + '/.timetracker/data.json', 'w')
	f.write(json.dumps(x))
	f.close()


def get_arg():
	result = ''
	for i in range(1, len(sys.argv)):
		result = result + sys.argv[i] + ' '
	return result.strip()


def log(x):
	f = open(path + '/.timetracker/log', 'a')
	f.write("(" + str(datetime.datetime.now()) + ") ")
	f.write(x)
	f.write("\n")
	f.close()


def parse_datetime(s):
	s = s.split(' ')
	s[0] = s[0].split('-')
	s[1] = s[1].split(':')
	s[1][-1] = s[1][-1].split('.')
	year = int(s[0][0])
	month = int(s[0][1])
	day = int(s[0][2])
	hour = int(s[1][0])
	minute = int(s[1][1])
	second = int(s[1][2][0])
	microsecond = int(s[1][2][1])
	return datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=microsecond)


def get_command(arg):
	if arg == '':
		return 'summary'
	commands = ['install', 'report', 'jobs', 'add', 'start', 'stop', 'remove']
	command = arg.split(' ')[0]
	if command in commands:
	  return command
	print "Unknown command"
	return -1


def get_current_working_jobs():
	data = load()
	status_dict = {}
	time_entries = data['time_entries']
	for te in time_entries:
		status_dict[te[0]] = te[1]
	active_ids = []
	for k in status_dict.keys():
		if status_dict[k] == 'start':
			active_ids.append(k)
	active = []
	for i in range(len(data['jobs'])):
		if data['jobs'][i]['id'] in active_ids:
			active.append(i)
	return active

# Operations

def install():
	try:
		os.mkdir(path + "/.timetracker")
	except:
		print 'Already installed!\n'
		return
	f = open(path + '/.timetracker/log', 'w')
	f.write("")
	f.close()
	data = {}
	data['jobs'] = []
	data['next_id'] = 0
	data['time_entries'] = []
	f = open(path + '/.timetracker/data.json', 'w')
	f.write(json.dumps(data))
	f.close()
	print 'Successfully installed!'


def summary():
	current = get_current_working_jobs()
	data = load()
	if len(current) == 0:
		print 'There are currently no active jobs.'
		return
	print '\n\nThe following jobs are currently active:\n'
	for j in current:
		print str(j+1) + ': ' + data['jobs'][j]['name']
	print '\n'

def report(arg):
	data = load()
	job_id = data['jobs'][arg-1]['id']
	entries = []
	for entry in data['time_entries']:
		if entry[0] == job_id:
			entries.append(entry)
	if len(entries) % 2 == 1:
		now = []
		now.append(job_id)
		now.append('stop')
		now.append(str(datetime.datetime.now()))
		entries.append(now)
	if len(entries) == 0:
		print 'No work has been done on this job.'
		return
	print '\n'
	print 'Report (' + data['jobs'][arg-1]['name'] + ')\n'
	total = 0
	today = 'None'
	today_date_string = str(datetime.datetime.now()).split(' ')[0]
	today_midnight_string = today_date_string + ' ' + '00:00:00.000000'
	for i in range(len(entries) / 2):
		if i == 0:
			total = parse_datetime(entries[1][2]) - parse_datetime(entries[0][2])
		else:
			total = total + (parse_datetime(entries[2*i+1][2]) - parse_datetime(entries[2*i][2]))
		if entries[2*i][2].startswith(today_date_string):
			if today == 'None':
				today = parse_datetime(entries[2*i+1][2]) - parse_datetime(entries[2*i][2])
			else:
				today = today + parse_datetime(entries[2*i+1][2]) - parse_datetime(entries[2*i][2])
		else:
			if entries[2*i+1][2].startswith(today_date_string):
				if today == 'None':
					today = parse_datetime(entries[2*i+1][2]) - parse_datetime(today_midnight_string)
				else:
					today = today + parse_datetime(entries[2*i+1][2]) - parse_datetime(today_midnight_string)
	print 'Time spent today: ' + str(today) + '\n'
	print 'Total time spent: ' + str(total) + '\n'

def jobs():
	data = load()
	print "\n"
	print "Jobs:\n\n"
	for i in range(len(data['jobs'])):
		print str(i+1) + ": " + data['jobs'][i]['name'] + "\n"

def add(arg):
	data = load()
	data['jobs'].append({})
	data['jobs'][-1]['id'] = data['next_id']
	data['jobs'][-1]['name'] = arg
	data['next_id'] = data['next_id'] + 1
	save(data)
	print "Job " + str(len(data['jobs'])) + " added."

def remove(arg):
	data = load()
	if arg < 1 or arg > len(data['jobs']):
		print 'There is no job with ID ' + str(arg) + '.'
		return
	data['jobs'].pop(arg-1)
	save(data)
	print 'Job ' + str(arg) + ' removed.'
	

def start(arg):
	if (arg-1) in get_current_working_jobs():
		print 'Job ' + str(arg) + ' is already active.'
		return
	data = load()
	info = []
	info.append(data['jobs'][arg-1]['id'])
	info.append('start')
	info.append(str(datetime.datetime.now()))
	data['time_entries'].append(info)
	save(data)
	print "Job " + str(arg) + " started."

def stop(arg):
	if (arg-1) not in get_current_working_jobs():
		print 'Job ' + str(arg) + ' is not active.'
		return
	data = load()
	info = []
	info.append(data['jobs'][arg-1]['id'])
	info.append('stop')
	info.append(str(datetime.datetime.now()))
	data['time_entries'].append(info)
	save(data)
	print "Job " + str(arg) + " stopped."



# Master

def do(arg):
	command = get_command(arg)
	if command == 'summary':
		summary()
	if command == 'install':
		install()
	if command == 'add':
		log(arg)
		arg = arg[3:].strip()
		add(arg)
	if command == 'jobs':
		jobs()
	if command == 'start':
		log(arg)
		arg = int(arg[5:].strip())
		start(arg)
	if command == 'stop':
		log(arg)
		arg = int(arg[4:].strip())
		stop(arg)
	if command == 'report':
		arg = int(arg[6:].strip())
		report(arg)
	if command == 'remove':
		log(arg)
		arg = int(arg[6:].strip())
		remove(arg)


if __name__ == "__main__":
	arg = get_arg()
	do(arg)
