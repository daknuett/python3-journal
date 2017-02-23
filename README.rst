jrnl - A Python3 journal management system
******************************************

The goal of this project is to create a 
system to manage journals for scientific research,
projects, experiments and trials.

**Warning**: This project is currently UNIX only!

Work so far
===========

- The complete model is implemented
- The system is in a working state
- The CLI works (there might be bugs)
- Basic exporting to markup works

TODOs
=====

- A search module
- A non CLI interface
- A better export system
- Export children
- Delete journals and entries
- Improve the CLI (autocomplete, history)

FIXMEs
======

- Trash unused archive files
- Trash unused file copys (if store_internal is true)
- Fix the journal IDs after creation
- Add help for datetimes

Usage
=====

You are able to install python3-journaly by cloning 
`<this repository> https://github.com/daknuett/python3-journal`_
Go to the base directory and run ``python3 -m jrnl.cli.cli``.
Then a installation helper will guide you through the installation process.
python3-journaly will be installed locally.

CLI
---

After installing python3-journaly you should be able to use
it using the executable you created. This will start a 
command line interface.

The most important commands are:

help
	A list of commands and the helptext.
help_create_entry
	A special helptext for create_entry.
create_journal
	Create a new journal. You will have to restart the program
	to use the new journal.
select <ID>
	Select and open the entry with the given ID.
create_entry
	Create a new entry in the selected journal.
lse
	List the entries in the selected journal.
lsj
	List the journals.
close 
	Save and close the current journal (You must run this after creating an entry).
save 
	Save the system (You must run this after creating a journal).
quit
	Quit the program.


Design
======

In order to make a flexible and yet simple system the following 
design has been developed. It is however no final design.
Therefore all classes have a version string.

`The System`_
	Provides an interface to the journals.
	The system is an internal API that might be used
	by different frontends, for example a CLI, a GUI or a Web interface.

`The Journal`_
	Is one journal. It contains some metadata and a list of entries.
	The journal can be converted to different storage formats (at least JSON)
	and several display formats (at least reStructuredText).

`The Entry`_
	Is one journal entry. It consists of a datetime, a heading, text and children.
	The datetime will be formatted as a string for storage.
	The children are a list of elements, like 

	- Images
	- Files
	- Videos

	The children can be stored as MIME base64 inside the journal file
	or external. The text includes a link to the child where it should be inserted.

`The Archive`_
	Is a list of entries. They are stored externally to decrease memory usage
	of large journals. Especially if store_internal is turned on the Entries will
	consume a lot of RAM because the filechildren are stored b64encoded in the Entry.

	The archives are stored in the same list as the entries and the entries can be loaded
	on demand.
	Archives are stored in external files and should be stored in the same directory as
	the journal.json file.


Data Format
===========

Usually the journal should be stored as JSON. 
Other formats could be supported but are optional.

All entries are stored within the journal storage file.

The Entry
=========

The text links to the children using the following formats:

- ``"["<heading> "|" <alttext> "|" <child_alias> "|" <child_type>"]"`` (version 0.0.1)
- ``"[!"<heading> "|" <alttext> "|" <child_alias> "|" <child_type>"]"`` to force the child to be stored in the same file (version 0.0.1)
- ``"[?"<heading> "|" <alttext> "|" <child_alias> "|" <child_type>"]"`` to force the child to be stored external (version 0.0.1)
- ``"[*"<heading> "|" <alttext> "|" <child_alias> "|" <child_type>"]"`` just add a link to the child (version 0.0.1)

For instance: 

- ``[This is a image | Example image | example.png | "image/png"]``
- ``[* Our data|A CSV file with the data| data.csv| "text/css"]``
- ``[! Fromula 1| Formula to calculate E_pot | formula01 | "latex"]``

If the entry contains any external data, there has to be a folder in the journal's directory for 
this entry. In this folder all external files are stored. Their name is the child_alias.

TODO: I still need to fix the children embedding stuff for ``jrnl.system.convert``.

The Journal
===========

Every journal has a storage file and, if any of the entries uses external files, 
a directory with the files. The directory should be zip'ed, if the journal is inactive.


The System
==========

The system is unique for every user. It contains a folder for every journal. 
In this folder is the journal storage file and the optional directory.

The system should not be zip'ed completely, but the journal directories might be zip'ed and
the zip file might be encrypted. Every journal will have a seperate encryption key.

On single user installations (for instance the CLI) there must be a directory
``~/.jrnl/`` containing at least ``installation.info`` with one line containing the
path of the installation, the default will be ``~/.jrnl``.

Other installation types (like a server installation) should create a meta instance
to manage systems.


The Archive
===========

Usually archiving ( ``system.preferences["archiving"]`` ) should be turned off,
but if you need it you can turn it on anyways.

The system will create a new archive if the journal.json grows over 5kb,
so really big journals (most propably over 700 archives) will create a new archive for every
entry.
You can expand archived entries in order to merge them to one archive.
