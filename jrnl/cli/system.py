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


	

