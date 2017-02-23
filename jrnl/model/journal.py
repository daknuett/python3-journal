#!/usr/bin/python3

import datetime
from .entry import Entry
from .archive import Archive
import os

class Journal(object):
	"""
	The representation of a journal.
	The attribute ``entries`` is a list of Entry and/or Archive objects.
	"""
	version = "0.0.1"
	def __init__(self, heading, datetime, description, authors, tags = [], need_storage = False):
		self.heading = heading
		self.authors = authors
		self.description = description
		self.datetime = datetime
		self.need_storage = need_storage
		self.timefmt = "%d.%m.%Y-%H:%M:%S"
		self.entries = []
		self.tags = tags

	def to_dict(self):
		return {"type": "journal", "version": self.version,
			"heading": self.heading, "authors": self.authors,
			"description": self.description, "datetime": self.datetime.strftime(self.timefmt),
			"need_storage": self.need_storage, "timefmt": self.timefmt,
			"tags": self.tags,
			"entries": [e.to_dict() for e in self.entries]}
	@staticmethod
	def from_dict(dct):
		"""
		Convert a dict to a Journal.

		Returns: The Journal
		"""
		
		if(not "type" in dct):
			raise Exception("malformed dictionary: no type field")
		if(dct["type"] != "journal"):
			raise Exception("dictionary does not describe a journal")
		major, minor, release = dct["version"].split(".")
		my_major, my_minor, my_release = Journal.version.split(".")

		# FIXME: find a better way to calculate this:
		major, minor, release = int(major), int(minor), int(release)
		my_major, my_minor, my_release = int(my_major), int(my_minor), int(my_release)

		version = major * 10000 + minor * 100 + release
		my_version = my_major * 10000 + my_minor * 100 + my_release
		if(version > my_version):
			raise Exception("journal version ({}) is too high. Current version: ({})".format(dct["version"], self.version))

		dtime = datetime.datetime.strptime(dct["datetime"], dct["timefmt"])
		journal = Journal(dct["heading"], dtime,
				dct["description"], 
				dct["authors"], 
				tags = dct["tags"],
				need_storage = dct["need_storage"])
		entries = []
		# load entries and archived entries.
		for entry in dct["entries"]:
			if(entry["type"] == "archive"):
				entries.append(Archive.from_dict(entry))
			elif(entry["type"] == "entry"):
				entries.append(Entry.from_dict(entry))
			
		journal.entries = entries
		return journal


	def add_entry(self, entry):
		"""
		Add a new entry.

		Returns: None
		"""
		self.entries.append(entry)
	def extract_all_archives(self, path):
		"""
		This will extract all archived entries, assuming that they are
		stored under ``path``. Then the journal will contain only entries.

		This will remove all archive files.
		"""
		archives = [e for e in self.entries if isinstance(e, Archive)]
		entries = [e for e in self.entries if not isinstance(e, Archive)]
		for archive in archives:
			archive.load(path)
			os.remove(os.path.join(path, archive.relpath))
			entries.extend(archive.entries)
		self.entries = sorted(entries, key = lambda x: x.datetime)
		
	def get_entry(self, heading):
		"""
		Get the entry with this heading.

		Returns: The Entry or None
		"""
		for entry in self.entries:
			if(entry.heading == heading):
				return  entry
		return None
		
	def search_entries(self, heading_contains):
		"""
		Search all entrys with ``heading_contains`` in the heading.
			

		Returns: list of entries 
		"""

		return [entry for entry in self.entries if heading_contains in entry.heading]
	

	def set_entry_by_number(self, number, new_entry):
		"""
		Sets the entry with the given number to new_entry.
		Will raise IndexError, if the number is not within the number of entries.
		TODO: code this

		Returns: None
		"""
		self.entries[number] = new_entry

	def set_entry_by_datetime(self, dtime, new_entry):
		"""
		Sets the entry with the given datetime dtime to new_entry
		Will raise an Exception if there is no such entry.	
		TODO: code this

		Returns: None
		"""
		pass
		

		
