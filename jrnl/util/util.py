#!/usr/bin/python3

from contextlib import contextmanager


def fs_compatible_name(string):
	"""
	Create a filesystem compatible name from ``string``.
	Used to create the storage paths.	
	Deletes all terminal escape characters and
	replaces " " and "\\\\t" with "_"

	Returns: The resulting name
	"""

	forbidden = "/\\\"'#*+(){}&"
	to_underscore = " \t"
	for char in to_underscore:
		string = string.replace(char, "_")
	for char in forbidden:
		string = string.replace(char, "")
	return string
	

@contextmanager
def open_closing(path, mode = "r"):
	"""
	Open the given path and close it again.
	"""
	f = open(path, mode)
	yield f
	f.close()

