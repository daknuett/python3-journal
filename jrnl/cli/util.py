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

