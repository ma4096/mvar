import pandas as pd
import numpy as np
import datetime
# Python Script zum table "abbrev.csv" sortieren und in tex-Table umformen

def toTexTable(s, h, f, makeHeader = True, vlines = False, hlines = True):
    # s: numpy-array with the data
    # h: list of the headers
    # f: filename to what it should be saved
    '''for i,r in enumerate(s):
        # wrap starter with $...$ if there is a \ (indicates special character)
        if "\\" in s[i][0]:
            s[i][0] = f"${s[i][0]}$"'''

    t = [] # main table into which each row gets printed as a string
    midrule = ""
    if hlines:
        midrule = "\\hline"

    headline = "\\begin{longtable}{p{.13\\textwidth} p{.1\\textwidth} p{.07\\textwidth} p{.70\\textwidth}}"
    if vlines:
        headline = "\\begin{longtable}{p{.1\\textwidth}|p{.1\\textwidth}|p{.1\\textwidth}|p{.70\\textwidth}}"

    t.append(headline)
    if makeHeader:
        t.append("&\t".join(h) + f"\\\\{midrule}")

    acdc = 0
    for i in s:
        if pd.isnull(i[3]):
            acdc += 1
            if acdc == 1:
                print("Catched mistakes or comments, not enough rows, maybe a tab missing?")
            continue
        if "_" in i[0]: # encase math names in math environment
            i[0] = f"${i[0]}$"

        t.append("&\t".join([str(j) for j in i]) + f"\\\\{midrule}")
    t.append("\\end{longtable}")
    
    with open(f"{f}.tex","w") as file:
        file.writelines("\n".join(t))
    return

def toTypstTable(s,f,h=None, vlines=False, hlines=True, bold_header=True, col_width=None,align="center", col_align=None, custom=""):
    """Creates a typst table from a numpy array and a list of headers and saves it to a .typ file

    :param s: numpy 2d array consisting of rows [name: str, val: str, unit: str, description: str]. They will be put into a typst [...] environment. For greek letters/math styling, encase with $..$, for further scripting start with #...
    :param f: str, path of the file to save to, e.g. abbrev.typ. Must include file ending ".typ". THIS FILE WILL BE OVERWRITTEN!
    :param h: optional list<str> of headers. Will be printed on top of the table. Default is None, results in no header printed. Must have as many entries as s has columns.
    :param vlines: optional bool, print vertical lines between columns. Default False.
    :param hlines: optional bool, print horizontal lines between rows. Default True
    :param bold_header: optional bool, make header column bold. Default True
    :param col_width: optional list<str>, give the width of each column as specified in typst documentation. Gets entered in to column argument of #table. Example: ["50%","10em","2in"]. Default is None, resulting in auto width for each column.
    :param align: optional str, how the table will be aligned on the page. To inherit from rest of the page, set to None. Default "center".
    :param col_align: optional list<str>, how each column will be aligned. Must have as many entries as there are columns. E.g. ["left","right","center"], uses typst keywords. Default None results in left for all. Outside #set table.cell(align: ...) overwrite this.
    :param custom: optional str, can be any set of typst command or whatever, gets put after the definition of the columns. For total customization, can be multiple lines. Default is "" (empty string)
    """
    n_col = s.shape[1] # number of columns that the table will have

    # safety checks
    if h != None and len(h) != n_col:
        raise ValueError(f"Length of h ({len(h)}) does not correspond with the number of columns in s ({n_col})")
        return
    if ".typ" != f[-4:]:
        raise ValueError(f"Filepath provided to save table to does not contain a .typ file extension. Filepath provided was {f} (the second argument)")
    if col_width != None and len(col_width) != n_col:
        raise ValueError(f"col_width list does not have the same number of entrances ({len(col_width)}) as there are columns ({n_col}).")
    if col_align != None and len(col_align) != n_col:
        raise ValueError(f"col_align list does not have the same number of entrances ({len(col_align)}) as there are columns ({n_col}).")

    col_width = col_width if col_width != None else ['auto' for i in range(n_col)]

    # define the stroke parameter for the typst table function. For guide on how to do that I recommend the typst table guide.
    stroke = "none" # 
    if hlines or vlines:
        stroke = f"""(x,y) => (
            {'top: if (y != 0) {{1pt}},' if hlines else ''}
            {'left: if (x != 0) {{1pt}}' if vlines else ''}
        )"""

    # define the align parameter
    col_align_string = ""
    if col_align != None:
        col_align_string = f"""
            align: ({', '.join(col_align)}),
        """

    # start of defining a typst table following typst documentation
    # define table_string which every row will get added to
    table_string = f"""// table generated via toTypstTable from makeAbbrev.py on {datetime.datetime.now()}
#table(
    columns: ({','.join(col_width)}),
    stroke: {stroke},
    {col_align_string}
    {custom}
    """

    # if a header is defined, add it as a line to the table_string 
    if h is not None:
        header_strings = [f"[{header}]" for header in h]
        if bold_header:
            header_strings = [f"[*{header}*]" for header in h]
        table_string += f"table.header({','.join(header_strings)}),\n"
    
    # normal table rows
    row_strings = []
    for row in s:
        row_strings.append("\t" + ",".join([f"[{i}]" for i in row]) + ",\n")

    # add the rows each as a new line and append closing bracket. If the table has an align environment, also close that with ]
    table_string += "".join(row_strings) + "\n)" + ("]" if align != None else "")

    table_string = (f"#align({align})[" if align != None else "") + table_string

    with open(f,"w") as file:
        file.write(table_string)
    print(f"makeAbbrev.py/toTypstTable() wrote a table to {f} which contained {len(s)} rows")
    return

def sortTable(t,col):
    """Sort a pandas dataframe by alpha-numerical order ascending. Ignores special characters $ or \

    :param t: pandas dataframe to get sorted. Must contain a header.
    :param col: name of the column to be sorted after. Must be in header of t.
    :return: the sorted and reindexed dataframe
    """

    #mt = t.applymap(lambda x: str(x).replace("$","").replace("\\","").upper())
    mt = t.map(lambda x: str(x).replace("$","").replace("\\","").upper())
    s = mt.sort_values(col)
    #print(s.index)
    return t.reindex(s.index)



if __name__ == "__main__":
    # just for testing
    #old = pd.read_csv("abbrev.csv",header=0,sep="\t")
    #s = list(old.sort_values("Zeichen").to_numpy())
    #print(s)
    #print(old.sort_values("Zeichen"))
    #headers = list(old)
    #print(old)
    #print(headers)
    #print(s.to_string(index=False))
    #s = sortTable(old,"Zeichen").to_numpy()

    #print(s_clean)
    #print(s)
    #toTexTable(s,headers,"abbrev")
    header = ["Name","Wert","Einheit","Beschreibung"]
    v = np.array([["variable 1",15,"m","the variable 1"],["$alpha_4$","acht","grad","Winkel"]])
    cols = ["13%","10%","10%","67%"]
    toTypstTable(v,"typst/abbrev.typ",h=header,col_width=cols,hlines=True, vlines=True, col_align=["right","left","center","left"])
    #print("written from abbrev.csv to abbrev.tex")
    #print(s)