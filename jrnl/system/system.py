#!/usr/bin/python3

import os, sys, json
from ..model.journal import Journal
from ..model.entry import Entry, Child
from zipfile import ZipFile
from ..util.util import fs_compatible_name


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

	def __init__(self, path, preferences = {},
			paths_by_id = {}, headings_by_id = {}, id_count = 0):
		self.path = path
		self.preferences = preferences
		self.paths_by_id = paths_by_id
		self.headings_by_id = headings_by_id
		self.id_count = id_count
		self.version = "0.0.1"

	def create_journal(self, heading, description, authors, 
			tags = [], dtime = "now", datetime_fmt = "%d.%m.%Y-%H:%M:%S", need_storage = False):
		"""
		Create a new journal.

		WARNING: this will just create the journal.
		In order to use it you must open_journal this journal.

		Returns: the journal_id
		"""
		path = os.path.join(self.path, fs_compatible_name(heading))
		os.path.makedirs(path)
		if(dtime == now):
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
			zipf = ZipFile(path + ".zip", "w")
			for dirname, subdirs, files in os.walk(path):
				zipf.write(dirname)
				for filename in files:
					zf.write(os.path.join(dirname, filename))
			zipf.close()

			os.rmdir(path)
		return self.id_count - 1

	def to_dict(self):
		"""
		Convert this system to a dict representation.
		"""
		return {"type": "system", "version": self.version, "path": self.path, 
			"preferences": self.preferences, "paths_by_id": self.paths_by_id,
			"headings_by_id": self.headings_by_id, "id_count": self.id_count}
		
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
		if(not os.path.exists(self.paths_by_id[id_])):
			if(os.path.exists(self.paths_by_id[id_] + ".zip")):
				f = ZipFile(self.paths_by_id[id_] + ".zip")
				f.extract_all(path = self.path)
			else:
				raise Exception("Journal not found: '{}' ('{}')".format(self.paths_by_id[id_],
							self.headings_by_id[id_]))
		with open_closing(os.path.join(self.paths_by_id[id_], statics["journal_file"])) as journal_file:
			journal = Journal.from_dict(json.load(journal_file))
		return journal

	def close_journal(self, journal):
		"""
		Close the journal by saving all data and zipping the directory,
		if self.preferences.zip_journals is set.

		Returns: None
		"""
		self.save_journal(journal)
		
		
		path = os.path.join(self.path, fs_compatible_name(heading))
		if("zip_journals" in self.preferences and self.preferences["zip_journals"]):
			# from http://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory/
			zipf = ZipFile(path + ".zip", "w")
			for dirname, subdirs, files in os.walk(path):
				zipf.write(dirname)
				for filename in files:
					zf.write(os.path.join(dirname, filename))
			zipf.close()

			os.rmdir(path)
		
		
	def save_journal(self, journal):
		"""
		Save the journal by copying all new files
		and writing the JSON files.

		Returns: None
		"""

		journal_path = os.path.join(self.path + fs_compatible_name(journal.heading))
		# save the children...
		for entry in journal.entries:
			if(entry.has_unsaved):
				entry_path = os.path.join(journal_path + statics["data_path"] + fs_compatible_name(entry.heading))
				if(not os.path.exists(entry_path)):
					os.makedirs(entry_path)
				for name, child in entry.children.items():
					if(child.unsaved):
						child.save(entry_path)
				entry.has_unsaved = False

		
		with open_closing(os.path.join(journal_path, statics["journal_file"]), "w") as journal_file:
			json.dump(journal.to_dict(), journal_file)
		
		
