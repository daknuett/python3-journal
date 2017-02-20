#!/usr/bin/python3

async def lse(session, inp, out, *args):
	if(session["current_journal"] == None):
		out.print("ERR: no journal selected")
		return

	select = "heading"
	if(len(args) > 0 and args[0] in ("datetime", "tags")):
		select = args[0]
	out.print("\t no:\t", select)
	for no, entry in enumerate(session["current_journal"].entries):
		out.print("\t", no, ":\t", getattr(entry, select))

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
	for field in to_print:
		out.print(field, "\t", getattr(entry, field))
