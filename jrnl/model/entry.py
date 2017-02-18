#!/usr/bin/python3

import base64, os
from ..util.util import open_closing

class Entry(object):
	"""
	A journal entry.
	"""
	def __init__(self, datetime, heading, text, tags = [], children = {}):
		self.version = "0.0.1"
		self.datetime = datetime
		self.heading = heading
		self.text = text
		self.children = children
		self.timefmt = "%d.%m.%Y-%H:%M:%S"
		self.tags = tags
		self.has_unsaved = False
	def to_dict(self):
		return {"type": "entry", "version": self.version,
			"datetime": self.datetime.strftime(self.timefmt),
			"timefmt": self.timefmt, 
			"heading": self.heading,
			"text": self.text,
			"tags": self.tags,
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
		my_major, my_minor, my_release = self.version.split(".")

		# FIXME: find a better way to calculate this:
		major, minor, release = int(major), int(minor), int(release)
		my_major, my_minor, my_release = int(my_major), int(my_minor), int(my_release)

		version = major * 10000 + minor * 100 + release
		my_version = my_major * 10000 + my_minor * 100 + my_release
		if(version > my_version):
			raise Exception("entry version ({}) is too high. Current version: ({})".format(dct["version"], self.version))

		dtime = datetime.datetime.strptime(dct["datetime"], dct["timefmt"])
		children = {k: Child.from_dict(v) for k,v in dct["children"].items()}

		return Entry(dtime, dct["heading"], dct["text"], tags = dct["tags"], children = children)
		
	
class Child(object):
	"""
	The base child object
	"""
	def __init__(self, name, alttext, embed = True):
		self.embed = embed
		self.name = name
		self.alttext = alttext
		self.version = "0.0.1"
		self.subclasstypes = {"filechild": FileChild, "renderchild": RenderChild}
		self.unsaved = False
	def to_dict(self):
		"""
		Convert this child to a dict object.
		"""
		return {"type": "child", "version": self.version, "name": self.name,
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
			if(not dct["type"] in self.subclasstypes):
				raise Exception("dictionary does not describe a child")
			self.subclasstypes[dct["type"]].from_dict(dct)
		major, minor, release = dct["version"].split(".")
		my_major, my_minor, my_release = self.version.split(".")

		# FIXME: find a better way to calculate this:
		major, minor, release = int(major), int(minor), int(release)
		my_major, my_minor, my_release = int(my_major), int(my_minor), int(my_release)

		version = major * 10000 + minor * 100 + release
		my_version = my_major * 10000 + my_minor * 100 + my_release
		if(version > my_version):
			raise Exception("child version ({}) is too high. Current version: ({})".format(dct["version"], self.version))
		return Child(dct["name"], dct["alttext"], embed = dct["embed"])

class FileChild(Child):
	"""
	Used to embed/insert files.

	If store_internal is True the content will be stored as a base64 encoded UTF-8
	string.
	"""
	def __init__(self, filename, dtype, name, alttext, embed = True, store_internal = False):
		Child.__init__(self, name, alttext, embed)
		self.filename = filename
		self.dtype = dtype
		self.store_internal = store_internal

	def save(self, path):
		"""
		Save the file under the given path, if store_internal is False.
		Will set self.filename to ``os.path.join(path, os.path.base_name(self.filename))``.
		"""
		real_filename = os.path.base_name(self.filename)
		path = os.path.join(path, real_filename)
		if(path == self.filename):
			return
		with open_closing(path, "wb") as to:
			with open_closing(self.filename, "rb") as from_:
				chunk_size = 10 ** 3
				done = False
				while(not done):
					chunk = from_.read(chunk_size)
					if(chunk == b""):
						done = True
					to.write(chunk)
		self.filename = path
		self.unsaved = False

	def to_dict(self):
		d = Child.to_dict(self)
		d.update({"type": "filechild", "dtype": self.dtype, 
				"store_internal": self.store_internal,
				"filename": self.filename})
		if(self.store_internal):
			f = open(self.filename, "rb")
			inp = f.read()
			f.close()
			d.update({"content": base64.b64encode(inp).decode("UTF-8")})
		return d
	@staticmethod
	def from_dict(dct):
		if(not "type" in dct):
			raise Exception("malformed dictionary: no type field")
		if(dct["type"] != "filechild" ):
			if(not dct["type"] in self.subclasstypes):
				raise Exception("dictionary does not describe a child")
			self.subclasstypes[dct["type"]].from_dict(dct)
		major, minor, release = dct["version"].split(".")
		my_major, my_minor, my_release = self.version.split(".")

		# FIXME: find a better way to calculate this:
		major, minor, release = int(major), int(minor), int(release)
		my_major, my_minor, my_release = int(my_major), int(my_minor), int(my_release)

		version = major * 10000 + minor * 100 + release
		my_version = my_major * 10000 + my_minor * 100 + my_release
		if(version > my_version):
			raise Exception("child version ({}) is too high. Current version: ({})".format(dct["version"], self.version))

		if(dct["store_internal"]):
			f = open(dct["filename"], "wb")
			f.write(base64.b64decode(dct["content"].encode("UTF-8")))
			f.close()

		return FileChild(dct["filename"], dct["dtype"], dct["name"], dct["alttext"], embed = dct["embed"])

class RenderChild(Child):
	"""
	Used to embed rendered data (for insance LaTeX)
	"""
	def __init__(self, data, dtype, alttext, embed = True):
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
			if(not dct["type"] in self.subclasstypes):
				raise Exception("dictionary does not describe a child")
			self.subclasstypes[dct["type"]].from_dict(dct)
		major, minor, release = dct["version"].split(".")
		my_major, my_minor, my_release = self.version.split(".")

		# FIXME: find a better way to calculate this:
		major, minor, release = int(major), int(minor), int(release)
		my_major, my_minor, my_release = int(my_major), int(my_minor), int(my_release)

		version = major * 10000 + minor * 100 + release
		my_version = my_major * 10000 + my_minor * 100 + my_release
		if(version > my_version):
			raise Exception("child version ({}) is too high. Current version: ({})".format(dct["version"], self.version))


		return RenderChild(dct["data"], dct["dtype"], dct["name"], dct["alttext"], embed = dct["embed"])



