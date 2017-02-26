"""
To reduce the size of journal files 
archive entries are used.

They will be created automatically by the journal in order to keep the
memory usage small.
"""

#
# Copyright(c) 2017 Daniel Knüttel
#

# This program is free software.
# Anyways if you think this program is worth it
# and we meet shout a drink for me.


#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Dieses Programm ist Freie Software: Sie können es unter den Bedingungen
#    der GNU Affero General Public License, wie von der Free Software Foundation,
#    Version 3 der Lizenz oder (nach Ihrer Wahl) jeder neueren
#    veröffentlichten Version, weiterverbreiten und/oder modifizieren.
#
#    Dieses Programm wird in der Hoffnung, dass es nützlich sein wird, aber
#    OHNE JEDE GEWÄHRLEISTUNG, bereitgestellt; sogar ohne die implizite
#    Gewährleistung der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.
#    Siehe die GNU Affero General Public License für weitere Details.
#
#    Sie sollten eine Kopie der GNU Affero General Public License zusammen mit diesem
#    Programm erhalten haben. Wenn nicht, siehe <http://www.gnu.org/licenses/>.



import datetime, os, json
from .entry import Entry
from ..util.util import fs_compatible_name, open_closing

class Archive(object):
	"""
	An archive that will

	- reduce the size of the journal file
	- reduce memory usage, if store_internal is True

	The archive(s) will be generated automatically if the
	system.preferences["archiving"] setting is true.
	Default is false, because it is still kind of buggy.
	"""
	version = "0.0.1"
	timefmt = "%d.%m.%Y-%H:%M:%S"
	def __init__(self, relpath, dtime_start, dtime_stop, entries = []):
		self.relpath = relpath
		self.datetime = dtime_start # just for compability
		self.dtime_start = dtime_start
		self.dtime_stop = dtime_stop
		self.entries = entries
		self.has_unsaved = False
	@staticmethod
	def from_entries(entries, path):
		"""
		Get the matching archive for the given list of entries.
		path should be the same path where the journal file is stored.
		The path will be used to store the archive.
		"""
		dtime_start = entries[0].datetime
		dtime_stop = entries[-1].datetime
		relpath = "archive-{}-{}.json".format(dtime_start.strftime(Archive.timefmt),
					dtime_stop.strftime(Archive.timefmt))
		archive =  Archive(relpath, dtime_start, dtime_stop, entries)
		archive.save(path)
		return archive
	def to_dict(self):
		return {"type": "archive", "version": Archive.version,
			"relpath": "archive-{}-{}.json".format(self.dtime_start.strftime(Archive.timefmt),
					self.dtime_stop.strftime(Archive.timefmt)),
			"dtime_start": self.dtime_start.strftime(Archive.timefmt),
			"dtime_stop": self.dtime_stop.strftime(Archive.timefmt)}
	def load(self, path):
		"""
		Load the entries from the archive file.
		The archive file must be under the given path.
		The path must not contain the archive file.
		For instance::

			path/to/journal/archive.json <- WRONG
			path/to/journal/             <- RIGHT
		"""
		path = os.path.join(path, self.relpath)
		with open(path) as f:
			entries = json.load(f)
			f.close()
		entries = [Entry.from_dict(d) for d in entries]
		self.entries = entries

	def save(self, path):
		"""
		Save the archive under the given path.
		The path must not contain the archive file.
		For instance::

			path/to/journal/archive.json <- WRONG
			path/to/journal/             <- RIGHT
		"""
		path = os.path.join(path, self.relpath)
		with open(path, "w") as f:
			json.dump([e.to_dict() for e in self.entries], f, indent = "\t")
			f.close()

		

	@staticmethod
	def from_dict(dct):
		"""
		"""
		
		if(not "type" in dct):
			raise Exception("malformed dictionary: no type field")
		if(dct["type"] != "archive"):
			raise Exception("dictionary does not describe a archive")
		major, minor, release = dct["version"].split(".")
		my_major, my_minor, my_release = Archive.version.split(".")

		# FIXME: find a better way to calculate this:
		major, minor, release = int(major), int(minor), int(release)
		my_major, my_minor, my_release = int(my_major), int(my_minor), int(my_release)

		version = major * 10000 + minor * 100 + release
		my_version = my_major * 10000 + my_minor * 100 + my_release
		if(version > my_version):
			raise Exception("archive version ({}) is too high. Current version: ({})".format(dct["version"], self.version))

		dtime_start = datetime.datetime.strptime(dct["dtime_start"], Archive.timefmt)
		dtime_stop = datetime.datetime.strptime(dct["dtime_stop"],  Archive.timefmt)

		archive = Archive(dct["relpath"], dtime_start, dtime_stop)
		return archive


