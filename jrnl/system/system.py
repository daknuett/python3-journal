#!/usr/bin/python3

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


import os, sys, json, datetime, shutil
from ..model.journal import Journal
from ..model.entry import Entry, Child
from ..model.archive import Archive
from zipfile import ZipFile
from ..util.util import fs_compatible_name, open_closing


statics = {
	"journal_file": "journal.json",
	"data_path": "data/",
	"system_file": "system.json"
}


class System(object):
	"""
	The interface to access journals.

	The system manages 

	- the journals
	- storage space
	- journal management (create, delete, store)
	"""
	version = "0.0.1"
	def __init__(self, path, preferences = {},
			paths_by_id = {}, headings_by_id = {}, id_count = 0):
		self.path = path
		self.preferences = preferences
		self.paths_by_id = paths_by_id
		self.headings_by_id = headings_by_id
		self.id_count = id_count
		

	def create_journal(self, heading, description, authors, 
			tags = [], dtime = "now", datetime_fmt = "%d.%m.%Y-%H:%M:%S", need_storage = False):
		"""
		Create a new journal.

		WARNING: this will just create the journal.
		In order to use it you must open_journal this journal.

		Returns: the journal_id
		"""
		path = os.path.join(self.path, fs_compatible_name(heading))
		os.makedirs(path)
		if(dtime == "now"):
			dtime = datetime.datetime.now()
		else:
			dtime = datetime.datetime.strptime(dtime, datetime_fmt)


		journal = Journal(heading, dtime, description, authors, tags = tags, need_storage = need_storage)
		
		self.paths_by_id[self.id_count] = fs_compatible_name(heading)
		self.headings_by_id[self.id_count] = heading
		self.id_count += 1

		if(need_storage):
			os.makedirs(os.path.join(path, statics["data_path"]))

		journal_file = open(os.path.join(path, statics["journal_file"]), "w")
		json.dump(journal.to_dict(), journal_file)
		journal_file.close()

		if("zip_journals" in self.preferences and self.preferences["zip_journals"]):
			# from http://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory/
			old_cwd = os.getcwd()
			os.chdir(self.path)
			zipf = ZipFile(path + ".zip", "w")
			for dirname, subdirs, files in os.walk(path):
				zipf.write(os.path.relpath(dirname, start = self.path))
				for filename in files:
					zipf.write(os.path.join(os.path.relpath(dirname, start = self.path), filename))
			zipf.close()
			os.chdir(old_cwd)

			shutil.rmtree(path)
		return self.id_count - 1

	def to_dict(self):
		"""
		Convert this system to a dict representation.
		"""
		return {"type": "system", "version": System.version, "path": self.path, 
			"preferences": self.preferences, "paths_by_id": self.paths_by_id,
			"headings_by_id": self.headings_by_id, "id_count": self.id_count}
	@staticmethod
	def from_dict(dct):
		if(not "type" in dct):
			raise Exception("malformed dictionary: no type field")
		if(dct["type"] != "system"):
			raise Exception("dictionary does not describe a entry")
		major, minor, release = dct["version"].split(".")
		my_major, my_minor, my_release = System.version.split(".")

		# FIXME: find a better way to calculate this:
		major, minor, release = int(major), int(minor), int(release)
		my_major, my_minor, my_release = int(my_major), int(my_minor), int(my_release)

		version = major * 10000 + minor * 100 + release
		my_version = my_major * 10000 + my_minor * 100 + my_release
		if(version > my_version):
			raise Exception("entry version ({}) is too high. Current version: ({})".format(dct["version"], self.version))
		return System(dct["path"], preferences = dct["preferences"],
			paths_by_id = dct["paths_by_id"], headings_by_id = dct["headings_by_id"], id_count = dct["id_count"])

		
	def dump(self):
		"""
		Write the system to the system storage file.
		"""
		with open(os.path.join(self.path, statics["system_file"]), "w") as f:
			json.dump(self.to_dict(), f)
			f.close()

	def open_journal(self, id_):
		"""
		Open the journal with the given ID.

		Returns: The Journal.
		"""
		if(not id_ in self.paths_by_id):
			raise Exception("unknown id: {}".format(id_))
		path = os.path.join(self.path, self.paths_by_id[id_])
		if(not os.path.exists(path)):
			if(os.path.exists(path + ".zip")):
				f = ZipFile(path + ".zip")
				f.extractall(path = self.path)
				f.close()
			else:
				raise Exception("Journal not found: '{}' ('{}')".format(path,
							self.headings_by_id[id_]))
		with open_closing(os.path.join(path, statics["journal_file"])) as journal_file:
			journal = Journal.from_dict(json.load(journal_file))
		return journal

	def close_journal(self, journal):
		"""
		Close the journal by saving all data and zipping the directory,
		if self.preferences.zip_journals is set.

		Returns: None
		"""
		self.save_journal(journal)
		
		
		path = os.path.join(self.path, fs_compatible_name(journal.heading))
		if("zip_journals" in self.preferences and self.preferences["zip_journals"]):
			# from http://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory/
			old_cwd = os.getcwd()
			os.chdir(self.path)
			zipf = ZipFile(path + ".zip", "w")
			for dirname, subdirs, files in os.walk(path):
				zipf.write(os.path.relpath(dirname, start = self.path))
				for filename in files:
					zipf.write(os.path.join(os.path.relpath(dirname, start = self.path), filename))
			zipf.close()
			os.chdir(old_cwd)

			shutil.rmtree(path)
		
		
	def save_journal(self, journal):
		"""
		Save the journal by copying all new files
		and writing the JSON files.

		Returns: None
		"""

		journal_path = os.path.join(self.path, fs_compatible_name(journal.heading))
		# save the children...
		for entry in journal.entries:
			if(entry.has_unsaved):
				entry_path = os.path.join(journal_path, statics["data_path"], fs_compatible_name(entry.heading))
				if(not os.path.exists(entry_path)):
					os.makedirs(entry_path)
				for name, child in entry.children.items():
					if(child.unsaved):
						child.save(entry_path)
				entry.has_unsaved = False

		if("archiving" in self.preferences and self.preferences["archiving"]):
			# archive the old&big entries
			if(len(json.dumps(journal.to_dict())) > 5*10**3): 

				# get lists of following entries
				entry_sets = []
				current_set = []
				for entry in journal.entries:
					if(isinstance(entry, Entry)):
						current_set.append(entry)
					else:
						if(current_set == []):
							continue
						entry_sets.append(current_set)
						current_set = []
				if(current_set != []):
					entry_sets.append(current_set)
				archives = [Archive.from_entries(entries, journal_path) for entries in entry_sets]
				archives.extend([e for e in journal.entries if isinstance(e, Archive)])
				archives = sorted(archives, key = lambda x: x.dtime_start)
				journal.entries = archives


		
		with open_closing(os.path.join(journal_path, statics["journal_file"]), "w") as journal_file:
			json.dump(journal.to_dict(), journal_file, indent = "\t")
		
		
