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
