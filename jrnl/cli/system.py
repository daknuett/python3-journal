#!/usr/bin/python3

from .util import get_authors, get_tags

async def create_journal(session, inp, out):
	"""
	Read userdata and create a new journal
	"""
	system = session["system"]
	created_journal = False
	while(not created_journal):
		out.print("Creating a new journal")
		data = {"datetime_fmt": "%d.%m.%Y-%H:%M:%S", "dtime": "now", "need_storage": False}
		data["heading"] = await inp.input_string("heading > ")
		data["description"] = await inp.input_string("description > ")
		data["authors"] = await get_authors(inp, out)
		data["tags"] = await get_tags(inp, out)
		while(await inp.input_char("is this information correct [Y/n]? ") in ("n", "N")):
			out.print("enter the wrong field name")
			out.print("fieldnames: ", [k for k,v in data.items()])
			fieldname = inp.input_string("fieldname > ")
			if(not fieldname in data):
				out.print("ERR: fieldname not recoginzed")
			else:
				if(fieldname == "authors"):
					data["authors"] = await get_authors(inp, out)
				if(fieldname == "tags"):
					data["tags"] = await get_tags(inp, out)
				else:
					data[fieldname] = await inp.input_type(type(data[fieldname]), fieldname + " > ")

		try:
			system.create_journal(data["heading"], data["description"], data["authors"],
					tags = data["tags"], dtime = data["dtime"], datetime_fmt = data["datetime_fmt"],
					need_storage = data["need_storage"])
			created_journal = True
		except Exception as e:
			out.print("Failed to create the journal: {}".format(e))
			if(not await inp.input_char("Retry [N/y]? ") in ("y", "Y")):
				created_journal = True
		
async def lsj(session, inp, out, *args):
	if("paths" in args):
		out.print("id", ":\t", "path")
		for id_, path in session["system"].paths_by_id.items():
			out.print(id_, ":\t", path)
	elif("headings" in args or True):
		out.print("id", ":\t", "heading")
		for id_, heading in session["system"].headings_by_id.items():
			out.print(id_, ":\t", heading)


	

