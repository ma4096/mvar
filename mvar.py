import configparser
import re
from collections import Counter
import makeAbbrev
import pandas as pd
import numpy as np
import sys

class mvar:
	def __init__(self, basePath, configPath="config.ini"):
		self.basepath = basePath
		# Loading configuration
		self.config = configparser.ConfigParser()
		self.config.read(configPath)
		self.delim = self.config["PARSER"]["delimiter"]

		self.basedir = "/".join(basePath.split("/")[:-1]) + "/"
		self.doctype = basePath.split(".")[-1]

	def getChildrenAndLoadvars(self, content, path):
		"""Scans the supplied content for flags of loaded transferfiles and other included files (nested)

		:param content: file-object/list<str> (from open(...) as f, pass f). This is the supplied content which will be crawled line by line
		:param path: str, path of the file which content is being scanned.
		:return: dictionary with keys "files" (list<str> of all paths of found files in the content) and "vars" (list<Transferfile Object> of found loadvariables-statements)
		"""
		# returns array of all paths of referenced files in content

		# get what is being searched for
		loaderC = []
		loaderV = ""
		comment = ""
		if self.doctype == "tex":
			loaderC = ["\\input{","\\include{"]
			loaderV = "\\loadvariables{" # \loadvariables{a}{...}
			comment = "%"
		elif self.doctype == "typ":
			loaderC = ["#include","#import"]
			loaderV = "loadvariables(" # #a = loadvariables(...)
			comment = "//"
		includeLines = []
		loadvarsLines = []
		for s in content:
			# keep everything infront of a comment, not yet known how to include multiline comment
			s = s.split(comment)[0]
			# since there are different ways it can be included in latex
			for l in loaderC:
				if l in s:
					includeLines.append(s)
			if loaderV in s and "\\verb|" not in s:
				# last one is an edge case were you are citing \loadvariables in a verbatim environment
				loadvarsLines.append(s)

		curdir = "/".join(path.split("/")[:-1]) + "/"

		includes = []
		loadvars = []
		if self.doctype == "tex":
			includes = [curdir + filterInputLatex(l) for l in includeLines]
			# here only basedir, because of how it is handled by latex...
			#loadvars = [self.basedir + filterLoadvarsLatex(l)["path"] for l in loadvarsLines]
			#path = self.basedir + filterLoadvarsLatex(l)["path"]
			#name = filterLoadvarsLatex(l)["name"]
			#originpath = curdir
			loadvars = [transferfile(curdir + filterLoadvarsLatex(l)["path"], filterLoadvarsLatex(l)["name"], path, self.basedir, delim=self.delim, doctype=self.doctype) for l in loadvarsLines]
		elif self.doctype == "typ":
			#print("Include Lines:", includeLines, loadvarsLines)

			includes = [curdir + line.split('"')[1] for line in includeLines]
			loadvars = [transferfile(curdir + filterLoadvarsTypst(l)["path"], filterLoadvarsTypst(l)["name"], path, self.basedir,delim=self.delim, doctype=self.doctype) for l in loadvarsLines]
		#print(loadvars)
		#, "names": [ for l in loadvarsLines]}
		print(f"getChildrenAndLoadvars() on {path} found {len(loadvars)} mentioned transferfiles: {loadvarsLines}")
		return {"files": includes, "vars": loadvars}

	def collect(self):
		print(f"Started collecting all loaded transferfiles in the project/document {self.basepath}")
		queue = [self.basepath]
		history = [self.basepath]
		loadvars = []

		excludes = ["mvar.typ"] # list of files which should not be crawled/scanned
		#names = []
		while len(queue) > 0:
			path = queue[0]
			try:
				with open(path, "r") as file:
					# this path ends up in the transferfile as originpath
					print(f"\nNow scanning {path}...")
					res = self.getChildrenAndLoadvars(file, path)
					loadvars += res["vars"]
					#names += res["names"]
					news = []
					for f in res["files"]:
						if f not in history and f.split("/")[-1] not in excludes:
							news.append(f)
					queue += news
					history += news
					print(f"Scanned {path}, newly added paths to the queue: {news}")
					queue.pop(0)
			except OSError:
				print(f"mvar: collect(): File {path} not found.")
				queue.pop(0)
			print(f"Remaining length of queue: {len(queue)}")

		#self.names = names
		self.loadvars = loadvars
		self.crawledfiles = history
		#print(loadvars)
		print(f"End of collection, found in total {len(loadvars)} loaded transferfiles when scanning {len(history)} files\n-------------------------------------------")

	def loadloadvars(self):
		print(f"Now loading a total of {len(self.loadvars)} transferfile:")
		self.total_num_of_vars = 0 # statistics :)
		for l in self.loadvars:
			self.total_num_of_vars += l.loadvars()
		print(f"Done loading all the transferfiles, found a total of {self.total_num_of_vars} variables.\n-------------------------------------------")

	def checkconflicts(self):
		# output warnings and errors if there are namespaces of loaded transferfiles used multiple times
		goodtogo = True
		varnames = []
		for l in self.loadvars:
			varnames += l.varnames()

		namespaces = [v.name for v in self.loadvars]

		# check if the namespaces are not equal
		if len(set(namespaces)) != len(namespaces):
			goodtogo = False
			doubles = ""
			for key,val in Counter(namespaces).items():
				if val != 1:
					for l in self.loadvars:
						if l.name == key:
							doubles += f"\n\t{l.name} for {l.path} in {l.originpath}"
			print(f"Error while collecting transfer files: A namespace is used multiple times! {doubles}")
		# check if the variable names are not equal, collect all names:
		elif len(set(varnames)) != len(varnames):
			print("Warning while collecting transfer files: A variable name is used multiple times")
			#goodtogo = False
			# is ok as long as user keeps track of the namespaces
		
		return goodtogo

	def makeabbrevtable(self, path=None):
		"""Build a table of abbreviations from all loaded transferfiles/variables/namespaces. This is heavily dependent on config.ini, where you set attributes like a header (in your language), escaped namespaces (that should not be included), etc. 

		:param path: optional str, filename/path to where it should be saved. Default None results in abbrev.typ/.tex in the root directory of the project.
		"""

		print(f"Now building the table of abbreviations.")
		# build abbrev table and safe it
		self.abbrev = {"exists": True}
		self.abbrev["sortc"] = self.config["ABBREV"]["coloumnsort"].split(" ")
		self.abbrev["sortr"] = self.config["ABBREV"]["sortby"]
		self.abbrev["coloumns"] = self.config["ABBREV"]["coloumnname"].split("|")
		self.abbrev["makeHeader"] = strtobool(self.config["ABBREV"]["header"])
		self.abbrev["vlines"] = strtobool(self.config["ABBREV"]["verticalLines"])
		self.abbrev["hlines"] = strtobool(self.config["ABBREV"]["horizontalLines"])
		
		# block certain namespaces from being included
		escape = self.config["ABBREV"]["escapeNamespace"].split("|")

		# collect all variables of all namespaces, which are not in the escape configuration, to one large table.
		tab = []
		for l in self.loadvars:
			if l.name not in escape:
				for v in l.content:
					if bool(re.match(r'[0-9](\.)?[0-9]*[e]?[\-]?[0-9]*$', v[1])):
						tab.append(v)
					elif v[1] == "-": # also enter abbreviation/variables without a value (default value -)
						tab.append(v)
			else:
				print(f"Namespace {l.name} has been excluded from list of abbreviations as per config.ini")
		
		print(f"A total of {len(tab)} variables fit the scheme, they either numerical (e.g. 'xx.xx' or 'xx.xx*e-xx.xx') or don't have a value ('-'), as they are abbreviations. A total of {self.total_num_of_vars-len(tab)} variables have been excluded, as they don't fit in the scheme")

		df_raw = pd.DataFrame(tab, columns=["name", "val", "unit", "description"])
		df = df_raw[self.abbrev["sortc"]]
		df = makeAbbrev.sortTable(df, self.abbrev["sortr"])
		df.columns = self.abbrev["coloumns"]
		# df: pandas dataframe with sorted coloumns 
		#print(tab, df_raw, df)
		if self.doctype == "tex":
			if path == None:
				path = f"{self.basedir}abbrev"
			tabletex = df.to_numpy()
			makeAbbrev.toTexTable(tabletex, self.abbrev["coloumns"], path, makeHeader=self.abbrev["makeHeader"], vlines=self.abbrev["vlines"], hlines=self.abbrev["hlines"])

		elif self.doctype == "typ":
			if path == None:
				path = f"{self.basedir}abbrev.typ"
				print(self.basedir)
			table = df.to_numpy()
			print()
			makeAbbrev.toTypstTable(table, path, h=self.abbrev["coloumns"], vlines=self.abbrev["vlines"], hlines=self.abbrev["hlines"], col_width=["13%","10%","10%","67%"],align="left")
		print(f"The table of abbreviations has been written to {path}.\n-------------------------------------------")


	def ziploadvariables(self, path=None):
		"""Export all loadvars into one file so it can be loaded centrally. This is useful for LaTeX documents, so you can reference variables/namespaces that where imported in other files in the same document. 
		But variables can also just be used after being loaded in the document, also in other files. Zipping is usefull if you want to move around chapters without worrying where to load the transferfiles, as it loads them all in the beginning.

		:param path: optional string, path to the file (with .tex/.typ extension) where the collection should be saved.
		"""
		content = ""
		if self.doctype == "tex":
			for l in self.loadvars:
				content += f"{l.tocommand()}\n"
			if path == None:
				path = f"{self.basedir}/loader_collection.tex"

		elif self.doctype == "typ":
			content = "not yet implemented for typst" # not yet implemented
			if path == None:
				path = f"{self.basedir}/loader_collection.typ"

		with open(path, "w") as f:
			f.write(content)
		#print(content)


class transferfile:
	# basically csv parser with bonus steps...
	def __init__(self, path, name, originpath, basedir, delim=",", doctype=None):
		self.path = path # path of this transferfile relative to the python script
		self.name = name # namespace name
		self.originpath = originpath # path of the doc with the reference to this transfer file rel to python script
		self.content = []
		self.delimiter = delim
		self.doctype = doctype
		self.basedir = basedir # dir of the main document main.tex/typ rel to the python script
		
		# relative path from the main doc to this transfer file:
		# this assumes that basedir starts the same as path!
		spath = path.split("/") # this is always longer than sdir
		sdir = basedir.split("/")
		diff = spath
		for i,p in enumerate(sdir):
			if diff[0] == sdir[i]:
				diff.pop(0)
		self.relpath = "./" + "/".join(diff)
	
	def loadvars(self):
		self.content = []
		with open(self.path, "r") as file:
			for l in file:
				self.content.append(l.strip("\n").split(self.delimiter)[0:4])
		print(f"Transferfile '{self.path}' for the namespace '{self.name}' contains these variables (total of {len(self.content)}): {[a[0] for a in self.content]}\n")
		return len(self.content) # for statistics :)

	def varnames(self):
		if len(self.content) == 0:
			print(f"This transferfile has no content or has not been loaded: {self.path}")
		return [l[0] for l in self.content]

	def tocommand(self, newpath=None):
		# newpath: if the command will be called from another then the standard directory, change the path. Not yet implemented!
		if self.doctype == None:
			print(f"Error: no doctype declared/detected for transferfile from {self.path} in initalisation of this transferfile object")
			return 0
		if self.doctype == "tex":
			return f"\\backgroundloadvariables{{{self.name}}}{{{self.relpath}}}"
		elif self.doctype == "typ":
			1+1 # not yet implemented




def filterInputLatex(s):
	# gets a string like ...\input{./abc/tes.tex}...
	# return only ./abc/tes.tex, where .tex is not guaranted
	li = re.split('{|}',s.strip("\t").strip("%").strip("\t"))
	index = 0
	if "\\input" in li:
		index = li.index("\\input") + 1
	else:
		index = li.index("\\include") + 1
	path = li[index].strip(".").strip("/")
	if ".tex" not in path:
		path += ".tex"
	return path

def filterLoadvarsLatex(s):
	li = re.split(r'{|}|\\',s)
	#print(li)
	index = li.index("loadvariables") + 3

	return {"path": li[index].removeprefix("./"), "name": li[index-2]}

def filterLoadvarsTypst(s):
	"""get a line like "#let a = loadvariables('test.txt')" and give the namespace and the path. Primarily used when loading/finding loadvariables uses in a typst doc. This parser is not perfect, please just use the loadvariables()-func just like this in your typ doc and just dont use spaces in your path/filenames...

	:param s: str of the line
	:return: dictionary with "name": str of the namespace (e.g. "a") and "path" of the file (e.g. "text.txt")
	"""
	a = s.split(" ")
	if len(a) != 4 and len(a) != 5:
		raise ValueError(f"mvar: filterLoadvarsTypst(): The line '{s}' doesn't follow the rules of how loadvariables should be used in a typst document, so it can't be parsed (this parser is bad :D). Please always load your transferfiles using exactly this structure, one per line: '#set a = loadvariables(\"folder/test.txt\")'. If your line seems similar, make sure the path to the transferfile does not have any spaces!")
	name = a[1]
	path = ""
	if '"' in a[3]:
		path = a[3].split('"')[1]
	else:
		path = a[3].split("'")[1]
	return {"name": name, "path": path}


def strtobool(val):
	# from https://stackoverflow.com/questions/715417/converting-from-a-string-to-boolean-in-python
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))

if __name__ == "__main__":
	args = sys.argv # for command line interface
	if len(args) == 1:
		print("Not enough arguments given, displaying help:")
		helpstr = '''Precompiler for the mvar system. Usage:
		mvar.py [doc] -na
		[doc]: file/path to your main document file (like ./folder/main.tex or main.typ)
		-na: no abbreviations, dont build a (new) list of abbreviations.
		manually configure the list of abbreviations in config.ini'''
		print(helpstr)
		quit()
	elif args[1] == "testing": # for testing during development
		tex = mvar("./latex/test.tex")
		typst = mvar("./typst/test.typ")
		#print(tex.doctype)
		#print(typst.doctype)
		#print(tex.basedir)
		tex.collect()
		print(tex.loadvars[1].path)
		tex.loadloadvars()
		#print(tex.checkconflicts())

		#tex.makeabbrevtable()
		tex.ziploadvariables()
		quit()

	# normal operation
	doc = mvar(args[1])
	doc.collect()
	doc.loadloadvars()
	doc.checkconflicts()
	doc.ziploadvariables()
	if not "-na" in args:
		doc.makeabbrevtable()