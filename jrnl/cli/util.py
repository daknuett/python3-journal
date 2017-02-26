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



from ..model.entry import FileChild, RenderChild
import os

async def get_authors(inp, out):
	out.print("Enter the authors (empty line to stop)")
	authors = []
	auth = "q"
	while(auth != ""):
		auth = await inp.input_string(" author > ")
		if(auth != ""):
			authors.append(auth)
	return authors

async def get_tags(inp, out):
	out.print("Enter the tags (empty line to stop)")
	tags = []
	tag = "q"
	while(tag != ""):
		tag = await inp.input_string(" tag > ")
		if(tag != ""):
			tags.append(tag)
	return tags


async def get_children(inp, out):
	out.print("Enter an empty name to stop")
	children = []

	constructors = {"filechild": __get_filechild, "renderchild": __get_renderchild}
	
	def get_valid_type(string):
		if(string in constructors):
			return string
		raise Exception("type must be in {}".format([k for k,v in constructors.items()])) 

	name = "q"
	while(name != ""):
		data = {}
		data["name"] = await inp.input_string(" name > ")
		name = data["name"]
		if(name == ""):
			break
		chtype = await inp.input_type(get_valid_type, " type > ")
		children.append(await constructors[chtype](inp, out, data))
	return children

async def __get_filechild(inp, out, data):
	data["filename"] = await inp.input_string(" filename > ")
	while( not os.path.exists(os.path.expanduser(data["filename"]))):
		data["filename"] = await inp.input_string(" filename [did not exist] > ")
	data["dtype"] = await inp.input_string(" dtype > ")
	data["alttext"] = await inp.input_string(" alttext > ")
	data["embed"] = await inp.input_type(bool, " embed > ")
	data["store_internal"] = await inp.input_type(bool, " store_internal > ")
	return FileChild(data["filename"], data["dtype"], data["name"],
			data["alttext"], embed = data["embed"], store_internal = data["store_internal"])

async def __get_renderchild(inp, out, data):
	data["data"] = await inp.input_string(" data > ")
	data["dtype"] = await inp.input_string(" dtype > ")
	data["alttext"] = await inp.input_string(" alttext > ")
	data["embed"] = await inp.input_type(bool, " embed > ")
	return RenderChild(data["data"], data["dtype"], data["alttext"], embed = data["embed"])

