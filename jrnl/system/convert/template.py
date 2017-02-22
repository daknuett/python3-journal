"""
Templates to convert journals to markup languages.
"""

class EntryTemplate(object):
	"""
	A template to convert entries to markup languages.

	- The str ``markuptype`` determines the output format (i.e. rst)
	- The list ``fields`` is a list of supported data fields
	- The str ``text`` is the actual template
	- The dict ``defaults`` contains default values if someone wants to
	  ignore those fields.

	Example:
	::

		templ = {"markuptype": "rst",
			"text":\
		'''

		{heading}
		============================================
		
		created by: {author}
		created on: {datetime}
		tags:       {tags}
		
		{text}	    

		''',
			"fields": ["heading", "author", "datetime", "tags", "text"],
			"defaults": {}
		}
		templ = EntryTemplate.from_dict(templ)

		data = {"author": "Me",
			"heading": "Foo Bar",
			"datetime": "12.12.12",
			"tags": [],
			"text": "This is just a small example"
		}
		print(templ.format(data))
	"""
	version = "0.0.1"
	def __init__(self, markuptype, text, fields, defaults = {}):
		self.markuptype = markuptype
		self.text = text
		self.fields = fields
		self.defaults = defaults
	def to_dict(self):
		return {"type": "entrytemplate", "version": EntryTemplate.version,
			"markuptype": self.markuptype, "text": self.text,
			"fields": self.fields, "defaults": self.defaults}

	@staticmethod
	def from_dict(dct):
		if(not "type" in dct):
			raise Exception("malformed dictionary: no type field")
		if(dct["type"] != "entrytemplate"):
			raise Exception("dictionary does not describe a entrytemplate")
		major, minor, release = dct["version"].split(".")
		my_major, my_minor, my_release = EntryTemplate.version.split(".")

		# FIXME: find a better way to calculate this:
		major, minor, release = int(major), int(minor), int(release)
		my_major, my_minor, my_release = int(my_major), int(my_minor), int(my_release)

		version = major * 10000 + minor * 100 + release
		my_version = my_major * 10000 + my_minor * 100 + my_release
		if(version > my_version):
			raise Exception("entrytemplate version ({}) is too high. Current version: ({})".format(dct["version"], self.version))

		return EntryTemplate(dct["markuptype"], dct["text"], dct["fields"], dct["defaults"])

	def format(self, **kwargs):
		fields = {k:v for k,v in kwargs.items() if k in self.fields}
		for field in self.fields:
			if(not field in kwargs):
				if(field in self.defaults):
					fields[field] = self.defaults[field]
				else:
					raise Exception("Required field missing: {}".format(field))
		return self.text.format(**fields)


class JournalTemplate(object):
	version = "0.0.1"
	def __init__(self, markuptype, text, fields, entry_template, defaults = {}):
		self.markuptype = markuptype
		self.text = text
		self.fields = fields
		self.defaults = defaults
		self.entry_template = entry_template
	def to_dict(self):
		return {"type": "journaltemplate", "version": JournalTemplate.version,
			"markuptype": self.markuptype, "text": self.text,
			"fields": self.fields, "defaults": self.defaults,
			"entry_template": self.entry_template.to_dict()}

	@staticmethod
	def from_dict(dct):
		if(not "type" in dct):
			raise Exception("malformed dictionary: no type field")
		if(dct["type"] != "journaltemplate"):
			raise Exception("dictionary does not describe a journaltemplate")
		major, minor, release = dct["version"].split(".")
		my_major, my_minor, my_release = JournalTemplate.version.split(".")

		# FIXME: find a better way to calculate this:
		major, minor, release = int(major), int(minor), int(release)
		my_major, my_minor, my_release = int(my_major), int(my_minor), int(my_release)

		version = major * 10000 + minor * 100 + release
		my_version = my_major * 10000 + my_minor * 100 + my_release
		if(version > my_version):
			raise Exception("journaltemplate version ({}) is too high. Current version: ({})".format(dct["version"], self.version))

		return JournalTemplate(dct["markuptype"], dct["text"], 
				dct["fields"], 
				EntryTemplate.from_dict(dct["entry_template"]),
				dct["defaults"])

	def format(self, **kwargs):
		fields = {k:v for k,v in kwargs.items() if k in self.fields}
		for field in self.fields:
			if(not field in kwargs):
				if(field in self.defaults):
					fields[field] = self.defaults[field]
				else:
					raise Exception("Required field missing: {}".format(field))

		if("authors" in fields):
			fields["authors"] = ", ".join(fields["authors"])
		if("entries" in fields):
			fields["entries"] = "".join([self.entry_template.format(**entry) for entry in fields["entries"]])
		
		return self.text.format(**fields)

default_entry_templates = {
	"rst":
		EntryTemplate.from_dict(\
		{
		"type": "entrytemplate",
		"version": "0.0.1",
		"markuptype": "rst",
		"text":\
'''

{heading}
--------------------------------------------

:created by: {author}  
:created on: {datetime}
:tags:       ``{tags}``

{text}	    

''',
			"fields": ["heading", "author", "datetime", "tags", "text"],
			"defaults": {}
		})
}

default_journal_templates = {
	"rst": JournalTemplate.from_dict(\
		{
		"type": "journaltemplate",
		"version": "0.0.1",
		"markuptype": "rst", 
		"fields": ["heading", "authors", "description", "datetime", "entries", "tags"],
		"text":\
'''
{heading}
*******************************************

:Authors:    {authors}
:created on: {datetime}
:tags:       ``{tags}``

Descrtipion
===========

{description}

Entries
=======

{entries}

''',
		"entry_template": default_entry_templates["rst"].to_dict(),
		"defaults": {}
		})

}


