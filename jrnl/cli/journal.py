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


from ..model.entry import Entry
from ..model.archive import Archive
import os
from ..util.util import fs_compatible_name, open_closing

async def lse(session, inp, out, *args):
	if(session["current_journal"] == None):
		out.print("ERR: no journal selected")
		return

	select = "heading"
	if(len(args) > 0 and args[0] in ("datetime", "tags")):
		select = args[0]
	out.print("\t no:\t", select)
	# FIXME: make this nicer.
	for no, entry in enumerate(e for e in session["current_journal"].entries):
		if(not isinstance(entry, Archive)):
			out.print("\t", no, ":\t", getattr(entry, select))
		else:
			out.print("\t", no, ":\t", "Archive from", entry.dtime_start, "to", entry.dtime_stop)

async def expand_archive(session, inp, out, *args):
	if(session["current_journal"] == None):
		out.print("ERR: no journal selected")
		return
	if(len(args) == 0):
		out.print("ERR: please enter an entry number")
		return
	try:
		entry = session["current_journal"].entries[int(args[0])]
	except Exception as e:
		out.print("ERR: unable to find entry with number:", args[0])
		out.print("     Exception was:", e)
		return
	if(not isinstance(entry, Archive)):
		out.print("ERR: no archive")
	
	journal_path = os.path.join(session["system"].path, fs_compatible_name(session["current_journal"].heading))
	entry.load(journal_path)
	# FIXME: this might start spamming your storage space with old archive files.
	entries = session["current_journal"].entries[:int(args[0])] + \
			entry.entries + \
			session["current_journal"].entries[int(args[0]) + 1:]
	session["current_journal"].entries = entries
	out.print("ok", len(entry.entries), "entries loaded")

async def print_entry(session, inp, out, *args):
	if(session["current_journal"] == None):
		out.print("ERR: no journal selected")
		return
	if(len(args) == 0):
		out.print("ERR: please enter an entry number")
		return
	fields = ("datetime", "author", "heading", "text", "tags")
	to_print = []
	for arg in args[1:]:
		if(arg in fields):
			to_print.append(arg)
		else:
			out.print("WARN: field not supported:", arg)
	if(to_print == []):
		to_print = fields
	try:
		entry = session["current_journal"].entries[int(args[0])]
	except Exception as e:
		out.print("ERR: unable to find entry with number:", args[0])
		out.print("     Exception was:", e)
		return
	if(not isinstance(entry, Archive)):
		for field in to_print:
			out.print(field, "\t", getattr(entry, field))
	else:
		out.print("ERR: Printing archives is not yet supported")
