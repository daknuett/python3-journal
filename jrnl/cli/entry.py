#!/usr/bin/python3
import os, aiofiles, datetime
from .util import get_tags, get_children
from ..model.entry import Entry

async def create_entry(session, inp, out):
	if(not session["current_journal"]):
		out.print("ERR: no journal selected")
		return

	editor = None
	if(not "EDITOR" in os.environ):
		editor = "vim"
	else:
		editor = os.environ["EDITOR"]

	out.print("Enter your Entry using", editor, ". Save the file and quit the editor when you are finished.")
	await inp.input_char("Press Enter to continue.")
	os.system(editor + " temp.entry")
	
	async with aiofiles.open("temp.entry") as f:
		text = await f.read()
		await f.close()
	os.remove("temp.entry")

	created = False
	while(not created):
		data = {"dtime": "now", "author": ""}
		data["heading"] = await inp.input_string("heading > ")
		data["tags"] = await get_tags(inp, out)

		correct = "n"
		while(correct in ("N", "n")):
			for k, v in data.items():
				out.print(k, ":\t", v)
			correct = await inp.input_char("Is this correct [Y/n]? ")
			if(not correct in ("N", "n")):
				break
			fieldname = await inp.input_string("Wrong fieldname > ")
			if(not fieldname in data):
				out.print("ERR: field not recognized")
				continue
			if(fieldname == "tags"):
				data["tags"] = await get_tags(inp, out)
			else:
				data[fieldname] = await inp.input_string(fieldname + " > ")
		if(await inp.input_char("Add children [N/y]? ") in ("Y", "y")):
			children = await get_children(inp, out)
		else:
			children = []
		for child in children:
			child.unsaved = True
		children = {c.name: c for c in children}

		try:
			if(data["dtime"] != "now"):
				dtime = datetime.datetime.strptime(data["dtime"], Entry.timefmt)
			else:
				dtime = datetime.datetime.now()
			entry = Entry(dtime, data["heading"], text, author = data["author"],
					tags = data["tags"], children = children)
			entry.has_unsaved = True
			session["current_journal"].add_entry(entry)

			created = True
		except Exception as e:
			out.print("ERR: ", e)
			if(not await inp.input_char("Retry [N/y]? ") in ("y", "Y")):
				created = True
	





	
