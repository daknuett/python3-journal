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
	





	
