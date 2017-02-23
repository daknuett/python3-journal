#!/usr/bin/python3
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
