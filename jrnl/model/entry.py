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

import base64, os, datetime
from ..util.util import open_closing

class Entry(object):
	"""
	A journal entry.
	"""
	version = "0.0.1"
	timefmt = "%d.%m.%Y-%H:%M:%S"
	def __init__(self, datetime, heading, text, author = "", tags = [], children = {}):
		self.author = author
		self.datetime = datetime
		self.heading = heading
		self.text = text
		self.children = children
		self.timefmt = Entry.timefmt
		self.tags = tags
		self.has_unsaved = False
	def to_dict(self):
		return {"type": "entry", "version": Entry.version,
			"datetime": self.datetime.strftime(self.timefmt),
			"timefmt": self.timefmt, 
			"heading": self.heading,
			"text": self.text,
			"tags": self.tags,
			"author": self.author,
			"children": {k: v.to_dict() for k,v in self.children.items()}}
	def add_child(self, child):
		"""
		Add a child.
		"""
		if(child.name in self.children):
			raise Exception("name already in usage: {}".format(child.name))
		self.children[child.name] = child
	@staticmethod
	def from_dict(dct):
		"""
		Construct an Entry from a dictionary.

		Returns: The Entry
		"""
		
		if(not "type" in dct):
			raise Exception("malformed dictionary: no type field")
		if(dct["type"] != "entry"):
			raise Exception("dictionary does not describe a entry")
		major, minor, release = dct["version"].split(".")
		my_major, my_minor, my_release = Entry.version.split(".")

		# FIXME: find a better way to calculate this:
		major, minor, release = int(major), int(minor), int(release)
		my_major, my_minor, my_release = int(my_major), int(my_minor), int(my_release)

		version = major * 10000 + minor * 100 + release
		my_version = my_major * 10000 + my_minor * 100 + my_release
		if(version > my_version):
			raise Exception("entry version ({}) is too high. Current version: ({})".format(dct["version"], self.version))

		dtime = datetime.datetime.strptime(dct["datetime"], dct["timefmt"])
		children = {k: Child.from_dict(v) for k,v in dct["children"].items() if not v == None}

		return Entry(dtime, dct["heading"], dct["text"], author = dct["author"], tags = dct["tags"], children = children)
		

class Child(object):
	"""
	The base child object
	"""
	version = "0.0.1"
	subclasstypes = {}
	def __init__(self, name, alttext, embed = True):
		self.embed = embed
		self.name = name
		self.alttext = alttext
		self.unsaved = False
	def to_dict(self):
		"""
		Convert this child to a dict object.
		"""
		return {"type": "child", "version": Child.version, "name": self.name,
			"embed": self.embed, "alttext": self.alttext}

	def save(self, path):
		"""
		Save the content of this child.
		Unused for non-file children.
		"""
		self.unsaved = False

	@staticmethod
	def from_dict(dct):
		"""
		Convert a dict object to a Child object.
		This will automatically invoke subclasses.

		TODO: Adapt this to 3.6 features
		FIXME: versionchecking		

		Returns: The Child
		"""
		
		if(not "type" in dct):
			raise Exception("malformed dictionary: no type field")
		if(dct["type"] != "child" ):
			if(not dct["type"] in Child.subclasstypes):
				raise Exception("dictionary does not describe a child")
			
			return Child.subclasstypes[dct["type"]].from_dict(dct)
		major, minor, release = dct["version"].split(".")
		my_major, my_minor, my_release = Child.version.split(".")

		# FIXME: find a better way to calculate this:
		major, minor, release = int(major), int(minor), int(release)
		my_major, my_minor, my_release = int(my_major), int(my_minor), int(my_release)

		version = major * 10000 + minor * 100 + release
		my_version = my_major * 10000 + my_minor * 100 + my_release
		if(version > my_version):
			raise Exception("child version ({}) is too high. Current version: ({})".format(dct["version"], Child.version))
		return Child(dct["name"], dct["alttext"], embed = dct["embed"])
	

class FileChild(Child):
	"""
	Used to embed/insert files.

	If store_internal is True the content will be stored as a base64 encoded UTF-8
	string.
	"""
	def __init__(self, filename, dtype, name, alttext, embed = True, store_internal = False, content = None):
		Child.__init__(self, name, alttext, embed)
		self.filename = filename
		self.dtype = dtype
		self.content = content
		self.store_internal = store_internal

	def save(self, path):
		"""
		Save the file under the given path, if store_internal is False.
		Will set self.filename to ``os.path.join(path, os.path.basename(self.filename))``.
		"""
		real_filename = os.path.basename(self.filename)
		path = os.path.join(path, real_filename)
		if(path == self.filename):
			return
		if(not self.store_internal):
			with open_closing(path, "wb") as to:
				with open_closing(os.path.expanduser(self.filename), "rb") as from_:
					chunk_size = 10 ** 3
					done = False
					while(not done):
						chunk = from_.read(chunk_size)
						if(chunk == b""):
							done = True
						to.write(chunk)
		else:
			with open_closing(os.path.expanduser(self.filename), "rb") as from_:
				self.content = base64.b64encode(from_.read()).decode("UTF-8")
		self.filename = path
		self.unsaved = False

	def to_dict(self):
		d = Child.to_dict(self)
		d.update({"type": "filechild", "dtype": self.dtype, 
				"store_internal": self.store_internal,
				"filename": self.filename,
				"content": self.content})
		return d
	@staticmethod
	def from_dict(dct):
		if(not "type" in dct):
			raise Exception("malformed dictionary: no type field")
		if(dct["type"] != "filechild" ):
			if(not dct["type"] in FileChild.subclasstypes):
				raise Exception("dictionary does not describe a child")
			FileChild.subclasstypes[dct["type"]].from_dict(dct)
		major, minor, release = dct["version"].split(".")
		my_major, my_minor, my_release = FileChild.version.split(".")

		# FIXME: find a better way to calculate this:
		major, minor, release = int(major), int(minor), int(release)
		my_major, my_minor, my_release = int(my_major), int(my_minor), int(my_release)

		version = major * 10000 + minor * 100 + release
		my_version = my_major * 10000 + my_minor * 100 + my_release
		if(version > my_version):
			raise Exception("child version ({}) is too high. Current version: ({})".format(dct["version"], FileChild.version))

		if(dct["store_internal"] and dct["content"]):
			f = open(dct["filename"], "wb")
			f.write(base64.b64decode(dct["content"].encode("utf-8")))
			f.close()

		return FileChild(dct["filename"], 
				dct["dtype"], 
				dct["name"], 
				dct["alttext"], 
				embed = dct["embed"], 
				store_internal = dct["store_internal"],
				content = dct["content"])

class RenderChild(Child):
	"""
	Used to embed rendered data (for instance LaTeX)
	"""
	def __init__(self, data, dtype, name, alttext, embed = True):
		Child.__init__(self, name, alttext, embed)
		self.dtype = dtype
		self.data = data

	def to_dict(self):
		d = Child.to_dict(self)
		d.update({"type": "renderchild", "dtype": self.dtype})

	@staticmethod
	def from_dict(dct):
		if(not "type" in dct):
			raise Exception("malformed dictionary: no type field")
		if(dct["type"] != "renderchild" ):
			if(not dct["type"] in RenderChild.subclasstypes):
				raise Exception("dictionary does not describe a child")
			RenderChild.subclasstypes[dct["type"]].from_dict(dct)
		major, minor, release = dct["version"].split(".")
		my_major, my_minor, my_release = RenderChild.version.split(".")

		# FIXME: find a better way to calculate this:
		major, minor, release = int(major), int(minor), int(release)
		my_major, my_minor, my_release = int(my_major), int(my_minor), int(my_release)

		version = major * 10000 + minor * 100 + release
		my_version = my_major * 10000 + my_minor * 100 + my_release
		if(version > my_version):
			raise Exception("child version ({}) is too high. Current version: ({})".format(dct["version"], RenderChild.version))


		return RenderChild(dct["data"], dct["dtype"], dct["name"], dct["alttext"], embed = dct["embed"])

Child.subclasstypes = {"filechild": FileChild, "renderchild": RenderChild}

