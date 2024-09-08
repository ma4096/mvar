# mvar
 Simple interface for numerical outputs (Python, Matlab) and documents (LaTeX, Typst). 
 This project is still in its very early stages and you may find comments like "not yet implemented" in the code as well as rudimentary test files in the directories. If you just want to interface between LaTeX and Matlab, feel free to use the (more stable) implementation in [matlab-latex-variables](https://github.com/ma4096/matlab-latex-variables). 

## Disclaimer
I am not a professional software developer and do this project for fun. This project tree is quite unorganized with each folder containing the implementation in the given language as well as examples and general testing I use in development. The root contains the precompiler.

## Motivation
When writing documentation of technical projects in latex, I often had to update values I got from calculations in Matlab (due to miscalculations or changed specifications). As this is boring and annoying work, I implemented these scripts/functions to be able to reference matlab variables directly in my documents so they update automatically. It grew to also accept input from Python and output to typst, an upcoming LaTeX alternative.
The name mvar originally comes from matlab variable.

## Usage
There are currently three parts: Some software/script (Python or Matlab) inputs variables into a transfer file (csv) which then get loaded/parsed into an output document-script (LaTeX or typst). In the document the variables can be referenced (details below) with or without the unit. 
Currently there is a precompilation needed to prevent namespace collisions and generate a list of abbrevations.

### Matlab
Put the function transfer.m into a folder in the Matlab PATH so Matlab can find it.
- For me (on Fedora 40 Linux) it is `/home/[user]/Documents/MATLAB`

In your Matlab script use
```transfer([file path], var1, ..., varN)```
where the variables can be numerical or symbolical. Symbolical (and matrices) get parsed to LaTeX format. Even plain text is possible, as long as it is not including a comma or linebreak, which would break the csv-parsing.
Boolean variables are converted into `1` (true) or `0` (false). 
I have not yet implemented a way to also store a unit or description (see transfer file), these are currently just added as "-,-". I strongly advise not to use this project to transfer symbolic equations from Matlab, as the used built-in parser to Matlab is not perfect.

### Python 
Include the python script `/python/mvar_transfer.py` in your python script (`from mvar_transfer import *`).

```python
v = mvariable("example.txt") # the path were you eventually want to store the transfer file
a = 10.2434 # example values
s = "abd"
v.add("a",a,"-","Abcd",sig=6) # add to transfer file with [name],[value],[unit],[description]. Also sets the number of significant digits to 6 (default is 4)
v.fastadd("s",s) # doesnt set [unit] and [description], they get the default value -

print(v.vars) # vars is a list with python dicts for each added variable
v.save() # writes the transfer file. Always completely rewrites the file!
```

### Transfer file
The file used by both parts. It is just a simple csv-file with `[name],[value],[unit],[description]` in each line. A `,` in any of these fields will lead to failure when parsing!
The default value for each field is `-`.

### LaTeX
Put the file `MLtransfer.tex` into your latex-projects folder (or use another path in the following command).
In a latex-file use
```
\input{MLtransfer.tex}
\input{loader_collection.tex} % generated during precompilation in the same directory as your main document
```
to access it. Variables can be imported from the file they have been saved to from Matlab using
```\loadvariables{[namespace]}{[file path]}```
- `[namespace]` is a prefix added to each variable. Can be used to have multiple variables from different files/scripts with the same name.
- `[file path]` includes the file extension (.txt) and can be relative path including changes in directory. e.g.:
	- `example.txt` if its in the same folder
	- `/subfolder/example.txt` if its in a sub folder
	- `../../otherfolder/example.txt` goes two folders back from original directory and into than into the new subfolder
- Unlimited files can be loaded, as long as they are using different namespaces. 

Finally imported variables can be used as 
```\mvar{[namespace]}{[var name]}```
- Don't forget to put (especially symbolical values) in a math environment like `$...$`
- e.g.: 
	- given the transfer file test.txt with the content `bar,123,m,Length of the bar`
	- `\loadvariables{foo}{test.txt}`
	- In the text: `\mvar{foo}{bar}` gives `123`
If you directly want to use the saved unit, use `\mvarsi{[namespace]}{[var name]}`. This puts the value and the unit of the variable into a SI-environment. Due to the `\SI`-macro in LaTeX, this only works on numerical values.

Saved boolean variables can be used with
```\mvaristrue{[namepsace]}{[var name]}{[text if true]}{[text if false]}```
where the used variable (from the given namespace) is checked to be 1. If it is 1, the expression evaluates as true and the correpsonding text is displayed (the text can include any latex code), if it is not 1, the other text repsectively is shown/returned. This can be useful for implementing an automatic documentation for used calculation "algorithms" (for me e.g. calculating screws after VDI 2230).

To include the list of abbreviations which was build during precompilation simply include the generated `abbrev.tex` in your document. You also must include the package `longtable` in your document header as `abbrev.tex` requires it.

### typst
The implementation of typst is still experimental and some features are not supported (like list of abbreviations), but the simple part works just fine :)

To use it, import `mvar.typ` into your project: 
```typst
#import "mvar.typ": *
// a is the namespace
#let a = loadvariables("test.txt") //a is like a python dict
Access variable named b via 
$ #a.b $
Access variable with unit (add si): //this can lead to nameconflicts if text.txt contains b and bsi
$ #a.bsi $
#mlogic(a.l,[true],[false]) // if a.l == 1 (true as specified for transfer file), do accordingly. [true] could also be more complex typst code without the [] ([false] as well)
```


### Precompilation (not finished!)
Precompilation is currently working and required for LaTeX but has not yet been implemented for typst.

Here the list of abbreviations is build from all the imported transfer files in a given document (LaTeX/typst), where the type of document is determined by the file extension.
Also all the imported transfer files are collected into a single file called `loader_collection.tex`, from where they are imported into the document at its compilation instead from all over the place inside the document to allow for cross references. This feature is still under construction and not fully working! 

To perform the precompilation execute `mvar.py` in your projects main directory:
``` python mvar.py main.tex ```
You can also skip generating the list of abbreviations by adding the flag `-na` (no abbreviation)
The configuration for list of abbreviations is specified in `config.ini` where you can edit the appearance/order of coloumns and rows (documented in place). It is only yet implemented for LaTeX and only includes numerical (scalar) variables or abbreviations which don't have a value (default value `-`). 

A precompilation is only needed when you include a new transfer file in your document tree, not if the data in the transfer files changes. If you are using the list of abbreviations you always need to precompile to update the list.

## Credits
The basic csv-parser is copied from Stackexchange user's Phelype Oleinik answer (edited by Mensch) with a lot of own additions. https://tex.stackexchange.com/questions/474397/populate-information-from-a-csv-file-into-a-latex-document-specifically-into-th/474404#474404 , last accessed May 20, 2024

The parser for Matlab matrices to latex notation is from Matlab user Lu Ce with minimal changes.
Lu Ce (2024). Matlab matrix to LaTeX conversion example (https://www.mathworks.com/matlabcentral/fileexchange/80629-matlab-matrix-to-latex-conversion-example), MATLAB Central File Exchange. Retrieved May 20, 2024. 


## Planned features/ideas
- Change from csv using comma as the separator to tab, allowing for more flexibility as what can be "transferred" (e.g. normal text). Currently LaTeX is not accepting it.
- Access elements of matrices/arrays directly. Currently they have to be manually saved as scalar values, as matrices are always shown in pmatrix-environments.
- Allow for all Matlab environment variables to be exported at once. It can get annoying with lots of variables, still less annoying than doing it by hand ;)
- Build a list of abbreviations for typst
- Build a variable explorer as an entirely own program (likely Python/tkinter based)
- Allow for unit and description to be specified in Matlab
- Change the way variables are exported in Matlab
- Some kind of handler for importing and exporting numerical values with statistical errors (e.g. m = 1.23+-0.05 kg)

If you have ideas for more features, feel free to contact me.