from ..system.convert.template import default_journal_templates
from ..util.util import fs_compatible_name, open_closing
import os

async def convert(session, inp, out):
	if(not session["current_journal"]):
		out.print("ERR: no journal selected")
		return

	journal_path = os.path.join(session["system"].path, fs_compatible_name(session["current_journal"].heading))
	session["current_journal"].extract_all_archives(journal_path)
	dtype = await inp.input_string("output format > ")
	if(not dtype in default_journal_templates):
		out.print("ERR: invalid output format")
		out.print("supported formats:", ", ".join([k for k,v in default_journal_templates.items()]))
		return
	filename = os.path.expanduser(await inp.input_string("output file > "))
	try:
		f = open(filename, "w")
	except Exception as e:
		out.print("Unable to open file:", e)
	f.write(default_journal_templates[dtype].format(**session["current_journal"].to_dict()))
	f.close()
	out.print("OK")
	out.print("resaving journal.")
	session["system"].save_journal(session["current_journal"])
	out.print("OK")
