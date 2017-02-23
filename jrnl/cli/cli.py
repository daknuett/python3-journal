#!/usr/bin/python3

from nuio.input.terminal import POSIXTerminalInput
from nuio.output.terminal import TerminalOutput
from ..util.util import open_closing
from ..system.system import System
import os, stat, json
import asyncio, aiofiles
from .system import create_journal, lsj
from .entry import create_entry
from .journal import lse, print_entry, expand_archive
from .convert import convert
from ..model.entry import *

"""
A CLI (Command Line Interface) for the
journal.
"""

version = "0.0.1"

default_prefs = {"zip_journals": True, "archiving": False}



async def make_init(inp, out):

	out.print("Welcome to python3-jrnl", version)
	out.print("There seems to be no configuration of python3-jrnl in your account.\n"
		"This initializor will help you to use python3-jrnl async with comfort.")
	
	cont = await inp.input_char("continue? [N/y] > ")
	if(not cont in ("y", "Y")):
		return 

	os.makedirs(os.path.expanduser("~/.jrnl"))

	out.print("If you have already set up this version of python3-jrnl enter 'c'")
	
	already_setup = await inp.input_char("Use an existing installation [N/c] > ")
	if(already_setup in ("c", "C")):
		path = await inp.input_string("Enter the path of the installation > ")
		path = os.path.expanduser(path)
		async with aiofiles.open(os.path.expanduser("~/.jrnl/installation.info"), "w") as f:
			await f.write(path)
			await f.close()
		return 

	out.print("You need to select the storage space for your journals.\n"
			"The default will be '~/.jrnl/'.")
	path = await inp.input_string("Path to the storage space (empty for default) > ")
	if(path.strip() == ""):
		path = "~/.jrnl"
	path = os.path.expanduser(path)
	if(not os.path.exists(path)):
		os.makedirs(path)

	out.print("The storage space has been created")
	#
	# XXX I do not know why but if I use aiofiles for this the write fails sometimes :-(
	#
	async with aiofiles.open(os.path.expanduser("~/.jrnl/installation.info"), "w") as f:
		await f.write(path)
		await f.close()


	out.print("Now you need to set your default preferences.")
	skip = await inp.input_char("Skip and keep all default values [/c] > ")
	preferences = {}
	if(not skip in ("c", "C")):
		for k,v in default_prefs.items():
			value = await inp.input_type(type(v), 
						prompt = k + " (default = {}) > ".format(v))
			preferences[k] = value
	else:
		preferences = default_prefs


	system = System(path, preferences)
	system.dump()
	out.print("The system has been created")

	executable = await inp.input_char("Do you want to create an executable? [N/y] > ")

	if(executable in ("y", "Y")):
		name = await inp.input_string("Enter the name of the executable > ")
		
		pythonpathext = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")

		async with aiofiles.open(os.path.expanduser(os.path.join("~/.jrnl/", name)), "w") as f:
			print(os.path.expanduser(os.path.join("~/.jrnl/", name)))
			await f.write("#!/bin/sh\nexport PYTHONPATH=$PYTHONPATH:{}\n\npython3 -m jrnl.cli.cli\n".format(pythonpathext))
			await f.close()
		st = os.stat(os.path.expanduser(os.path.join("~/.jrnl/", name)))
		os.chmod(os.path.expanduser(os.path.join("~/.jrnl/", name)), st.st_mode | stat.S_IEXEC)

		path_to_sh_rc = await inp.input_string("Enter the path to your .shrc (empty to skip)(like ~/.bashrc) > ")
		if(path_to_sh_rc.strip() != ""):
			async with aiofiles.open(os.path.expanduser(path_to_sh_rc), "a") as f:
				await f.write("\n\n# binary for python3-jrnl\nexport PATH=$PATH:{}\n\n".format("~/.jrnl/"))
				await f.close()

	out.print("You should now be able to use python3-jrnl")

async def mainloop(session, commands, helps, inp, out):
	out.print("help or h for a quick helptext")
	helps["quit"] = "Quit the mainloop"
	while(1):
		command = await inp.input_string("jrnl > ")
		if(len(command.split()) == 0):
			continue
		if(command.split()[0] == "quit"):
			return
		if(not command.split()[0] in commands):
			out.print("ERR: command not recognized:", command.split()[0])
			out.print("help or h for a quick helptext")
			continue
		await commands[command.split()[0]](session, inp, out, *(command.split()[1:]))

async def save(session, inp, out, *args):
	session["system"].dump()
	out.print("Saved the system")

async def select(session, inp, out, *args):
	system = session["system"]
	if(len(args) == 0):
		out.print("ERR: no id specified")
		return
	id = args[0]
	try:
		session["current_journal"] = system.open_journal(id)
		out.print("Opened journal", "'", session["current_journal"].heading, "'")
	except Exception as e:
		out.print("ERR: ", e)

async def help_create_entry(session, inp, out, *args):
	text = '''\
Creating a new entry is done in three steps:

- Create the text
  python3-journal will open $EDITOR (or vim) 
  and you will be able to enter the text you want to store.
  You can link to children using the following formats:

	- ``"["<heading> "|" <alttext> "|" <child_alias> "|" <child_type>"]"`` (version 0.0.1)
	- ``"[!"<heading> "|" <alttext> "|" <child_alias> "|" <child_type>"]"`` to force the child to be stored in the same file (version 0.0.1)
	- ``"[?"<heading> "|" <alttext> "|" <child_alias> "|" <child_type>"]"`` to force the child to be stored external (version 0.0.1)
	- ``"[*"<heading> "|" <alttext> "|" <child_alias> "|" <child_type>"]"`` just add a link to the child (version 0.0.1)

  (Warning: currently the explicit storage/embedding markers are being ignored)

  If you are done writing the text just save and close the file. (wq)

- Enter the metadata
  Like the date, author, heading and tags.
  You can enter an empty datetime. This will use the current date and time.

- Enter the children
  Children are non-text ressources you might want to use,
  like images, LaTeX or data.
  Currently there are two types of children:

	- filechild: to store files (dtype might be image/png or text/csv, ...) 
	- renderchild: to store rendered text (dtype might be text/latex)

  Just enter the name of the child (the same as child_alias) and either filechild or renderchild to select the child type.
  
- To save the changes use the commands "close" and "save" (in this order).

'''
	out.print(text)
	
async def close(session, inp, out, *args):
	if(not session["current_journal"]):
		out.print("ERR: no open journal")
		return
	session["system"].close_journal(session["current_journal"])
	session["current_journal"] = None
	out.print("OK")

async def inject(session, inp, out, *args):
	cmd = await inp.input_string("command > ")
	try:
		eval(cmd)
	except Exception as e:
		out.print("ERR:", e)

if __name__ == "__main__":
	out = TerminalOutput()
	inp = POSIXTerminalInput(out)

	loop = asyncio.get_event_loop()
	if(not os.path.exists(os.path.expanduser("~/.jrnl/installation.info"))):
		loop.run_until_complete(make_init(inp, out))

	session = {"open_journals": {}, "current_journal": None}
	path = open(os.path.expanduser("~/.jrnl/installation.info")).read()
	dct = json.loads(open(os.path.join(path, "system.json")).read())

	session["system"] = System.from_dict(dct)
	commands = {"create_journal": create_journal,
		"help_create_entry": help_create_entry,
		"create_entry": create_entry,
		"print_entry": print_entry,
		"expand_archive": expand_archive,
		"select": select,
		"convert": convert,
		"close": close,
		"save": save,
		"lse": lse,
		"inject": inject,
		"lsj": lsj
	}
	helps = {"help": "Print this help text",
		"create_entry": "Create a new Entry in the current journal",
		"help_create_entry": "Help about the create_entry command",
		"print_entry": "print_entry entryno {field}: print the entry",
		"expand_archive": "expand_archive <entryno> enxpand the archive <entryno>",
		"lsj": "lsj [headings|paths]: list the journals",
		"lse": "lse [heading|datetime|description|tags]: list the entries",
		"save": "Save the System",
		"select": "Open a journal to use it",
		"close": "Close the current journal",
		"convert": "Convert the journal to a markup file",
		"inject": "Eval one command. A hacky command for debugging.",
		"create_journal": "Create a new journal"
	}
	async def help(session, inp, out, *args):
		out.print("Help for python3-journal")
		for k, v in helps.items():
			out.print("\t", k, ":\t", v)
	commands["help"] = help
	commands["h"] = help

	loop.run_until_complete(mainloop(session, commands, helps, inp, out))
	async def test(session, inp, out):
		system = session["system"]
		session["current_journal"] = system.open_journal("0")
		current_journal = session["current_journal"]
		child1 = FileChild("/home/daniel/_DSC0031.JPG", "image/jpg", "img01", "Image 1", True, True)
		child2 = RenderChild("x \in \mathbb{R}", "text/latex", "formula01","x from real", True)
		entry = Entry(datetime.datetime.now(), "Test 3", "[Image|An image|img01|image/jpg]\n[Formula|A Fromula|formula01|text/latex]")
		entry.add_child(child1)
		entry.add_child(child2)
		current_journal.add_entry(entry)
		await close(session, inp, out)
		await save(session, inp, out)

#	loop.run_until_complete(test(session, inp, out))


	loop.close()


