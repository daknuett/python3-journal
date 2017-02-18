#!/usr/bin/python3

from nuio.input.terminal import POSIXTerminalInput
from nuio.output.terminal import TerminalOutput
from ..util.util import open_closing
from ..system.system import System
import os, stat
import asyncio, aiofiles

"""
A CLI (Command Line Interface) for the
journal.
"""

version = "0.0.1"

default_prefs = {"zip_journals": True}



async def make_init():
	out = TerminalOutput()
	inp = POSIXTerminalInput(out)

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
		
		async with aiofiles.open(os.path.expanduser(os.path.join("~/.jrnl/", name)), "w") as f:
			print(os.path.expanduser(os.path.join("~/.jrnl/", name)))
			await f.write("#!/bin/sh\n\npython3 -m jrnl.cli.cli\n")
			await f.close()
		st = os.stat(os.path.expanduser(os.path.join("~/.jrnl/", name)))
		os.chmod(os.path.expanduser(os.path.join("~/.jrnl/", name)), st.st_mode | stat.S_IEXEC)

		path_to_sh_rc = await inp.input_string("Enter the path to your .shrc (empty to skip)(like ~/.bashrc) > ")
		if(path_to_sh_rc.strip() != ""):
			async with aiofiles.open(os.path.expanduser(path_to_sh_rc), "a") as f:
				await f.write("\n\n# binary for python3-jrnl\nexport PATH=$PATH:{}\n\n".format("~/.jrnl/"))
				await f.close()

	out.print("You should now be able to use python3-jrnl")



if __name__ == "__main__":

	loop = asyncio.get_event_loop()
	if(not os.path.exists(os.path.expanduser("~/.jrnl/installation.info"))):
		loop.run_until_complete(make_init())

	loop.close()


