jrnl - A Python3 journal management system
******************************************

The goal of this project is to create a 
system to manage journals for scientific research,
projects, experiments and trials.

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

