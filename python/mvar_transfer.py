# write out to transferfiles for the mvar system
class mvariable:
	all_mentions = []
	basepath = ""

	def __init__(self, path):
		self.path = path
		self.vars = []
		if path not in self.all_mentions:
			self.all_mentions.append(path)
		else:
			print(f"Collection of variables in this script to path '{path}' already exists")
			raise Exception(f"Path {path} already in use by another instance of mvariable in this script")

	def add(self, name, val, unit, description, sig=4):
		var = {}
		var["name"] = name
		if type(val) == float:
			var["val"] = f'{float(f"{val:.{sig}g}"):g}'
		if type(val) == bool:
			if unit == "logic":
				var["val"] = 1 if val else 0
			else:
				print(f"""Logical value (boolean) {name} without the unit 'logic' detected.
				Use 'logic' if you want to use this variable in a document to logically select textblocks""")
				var["val"] = str(val)
		else:
			var["val"] = str(val)
		var["unit"] = unit
		var["description"] = description
		self.vars.append(var)

	def fastadd(self, name, val, unit="-", description="-",sig=4):
		self.add(name, val, unit, description, sig=sig)

	def save(self):
		with open(self.path, "w") as f:
			lines = [f"{v['name']},{v['val']},{v['unit']},{v['description']}" for v in self.vars]
			f.writelines(lines)

if __name__ == "__main__":
	v = mvariable("testP.txt")
	
	a = 10.24558
	s = "abc"

	v.add("a",a,"-","Abcd",sig=6)
	v.fastadd("s",s)

	print(v.vars)
	v.save()