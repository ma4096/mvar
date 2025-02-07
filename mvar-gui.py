import tkinter as tk
from tkinter import ttk, Text, Menu, font
from tkinter import filedialog as fd
from mvar import * # must be in the same directory
import webbrowser # for navigating to the github for help

fontsize = 12

def select_file():
	filetypes = (
		('All files', '*.*'),
		('text files', '*.txt')
	)

	filename = fd.askopenfilename(
		title='Open a file',
		initialdir='./',
		filetypes=filetypes,
	)

	print(f"Selected file: {filename}")
	doc = mvar(filename)
	doc.collect()
	doc.loadloadvars()
	tabs = doc.loadvars
	print(f"Amount of found transferfiles: {len(tabs)}")
	for tf in doc.loadvars:
		print(f"{tf.name} : {tf.path}")
		#tabs.append()

	update_tabs(tabs)

	return filename

def update_tabs(tabs):
	# deletes all old tabs and adds the new ones
	for old_tab in notebook.winfo_children():
		old_tab.destroy()
	print("Old tabs destroyed")
	#print(tabs)
	for m,tf in enumerate(tabs):
		tab_title = f"{tf.name}"
		print(f"Placing tab {tab_title}")
		tab = ttk.Frame(notebook, width=400, height=280)
		

		for y, entry in enumerate(tf.content):
			for x, celldata in enumerate(entry):
				cell = Text(tab, height=3, width=20)
				cell.grid(column=x, row=y)
				#print(celldata)
				cell.insert("1.0",celldata)
				# retrieve with text_content = cell.get('1.0','end')


		tab.pack(fill="both", expand=True)
		notebook.add(tab, text=tab_title)
	return

def help_github():
	webbrowser.open("https://github.com/ma4096/mvar")
	return

root = tk.Tk()
root.geometry("600x600")
root.title("mvar")
root.config(cursor="arrow")
#root.option_add("*Label.Font", f"helvetica {fontsize} bold") # from https://stackoverflow.com/questions/62558581/tkinter-default-font-is-tiny -> doesnt work for the filedialog? Only setting display scaling in Fedora to 100% instead of 125% fixes -> except for cursor, that needs the fix above ^^
print(root.tk.exprstring('$tcl_library'))
print(root.tk.exprstring('$tk_library'))

default_font = font.nametofont("TkDefaultFont")
default_font.configure(size=fontsize)
text_font = font.nametofont("TkFixedFont")
text_font.configure(size=fontsize)
fixed_font = font.nametofont("TkMenuFont")
fixed_font.configure(size=fontsize)

# MENUBAR
menubar = Menu(root)
root.config(menu=menubar)
menubar.config(cursor="arrow")

# FILE MENU
file_menu = Menu(menubar, tearoff=False)
file_menu.add_command(
	label="Select doc",
	command=select_file
)
menubar.add_cascade(
	label="File",
	menu = file_menu
)

# HELP MENU
help_menu = Menu(menubar, tearoff=False)
help_menu.add_command(
	label="Github",
	command=help_github
)
menubar.add_cascade(
	label="Help",
	menu = help_menu
)


# NOTEBOOK TABS
# Tabs are added when loading a doc
notebook = ttk.Notebook(root)
notebook.pack(expand=True)

#frame1 = ttk.Frame(notebook, width=400, height=280)
#frame2 = ttk.Frame(notebook, width=400, height=280)

#frame1.pack(fill="both", expand=True)
#frame2.pack(fill="both", expand=True)

#notebook.add(frame1, text="gsrafgseg1")
#notebook.add(frame2, text="gsrafgseg2")



root.mainloop()