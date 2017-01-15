# -*- coding: utf-8 -*-
import os
import psutil

from utils import bytes2human


def nicer_byte(nt):
	d = {}

	for name in nt._fields:
		value = getattr(nt, name)
		if name != 'percent':
			value = bytes2human(value)
		d[name] = value

	return d


def system_info():
	"""System info."""

	percs = psutil.cpu_percent(interval=0, percpu=True)
	cpus = {}
	for cpu_num, perc in enumerate(percs):
		name = str(cpu_num)
		cpus[name] = perc

	return {
		"cpus": cpus,
		"memory": nicer_byte(psutil.virtual_memory())
	}


def restart():
	"""Restart device."""
	return os.popen("/usr/bin/sudo /bin/systemctl reboot").read()


def shutdown():
	"""Shutdown device."""

	return os.popen("/usr/bin/sudo /bin/systemctl poweroff").read()
