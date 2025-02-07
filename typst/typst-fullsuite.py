# Addon to mvar.py 
# Writes a typst-dictionary to a given .typ-file (path) and compiles the .typ

# to use:
# write your typst neraly as usual with mvar-variables using namespace "m" and importing mvar as usual (see README.md).
# ALWAYS use "#m..a" instead of "#m.a", otherwise you cant preview your typst document before final compiling.
# place the flag //__fullsuite__ where you wish the variables to be loaded (optimally just after loading all packages)
import subprocess

flag = "//__fullsuite__"

def typst_fullsuite(tpath, var, save=None):
	"""Take input from a Python script and output a PDF based on a specified typst template.

	:param tpath: str path to a typst file like "/dir/template.typ". The file has to be structured as described in mvar documentations
	:param var: list of variables like [["name",1,"unit","description"],["name2","Value","logic","this is a string"]. Use "logic" as unit for string values.
	:param save: optional str, path to where the output .pdf should be saved to. Must end in ".pdf". Standard value is the tpath as pdf 
	"""
	flag = "//__fullsuite__"
	# type checking: tpath must include .typ ending
	if ".typ" not in tpath:
		print(f"first argument tpath must include .typ file ending, given was {tpath}")
		raise ValueError(f"typst fullsuite: first argument tpath must include .typ file ending, given was {tpath}")
		return ""

	# save: optionally specify the pdf file name and place, otherwise it will just get placed in the same directory as tpath.
	if save==None:
		save = tpath[0:-4] + ".pdf"
	presave = tpath[0:-4] + "-precompiled.typ"

	if len(var) < 2: # typst does not accept a 2D array with only one row
		var.append(["this_is_not_a_real_variable_rather_a_filler_due_to_typst_problems",-1,"-","-"])

	#vs = [[print(x) for x in r] for r in var]
	vs = ["(" + ','.join([f'"{x}"' for x in r]) + ")" for r in var]

	var_as_string = f'''#let m = parse_dict(({",".join(vs)}))'''
	lines = ""
	with open(tpath,"r") as file:
		lines = file.read()
		lines = lines.replace(flag, var_as_string)
		lines = lines.replace("#m..", "#m.")
		#file.write(lines)

	with open(presave,"w") as file:
		file.write(lines)

	# final compilation of pdf
	print(f"mvar: typst fullsuite subprocess executes the command: typst compile {presave} {save}")
	subprocess.run(["typst", "compile", presave, save])

	# cleanup
	subprocess.run(["rm", "-r", presave]) # delete temporary file
	try:
		subprocess.run(["rm","-r", f"{presave[:-4]}.pdf"])
	except Exception:
		print(f"typst fullsuite: tried to remove {presave[:-4]}.pdf, file not found. This doesn't have to be an error.")
	return save # returns saved path
	

if __name__=="__main__":
	# tests
	var = [["a",3,"m","Länge"]]
	typst_fullsuite("fullsuite-test.typ",var)