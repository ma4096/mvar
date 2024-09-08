import pandas as pd
import numpy as np
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

def sortTable(t,row):
    # cut off special characters like $ $ or \ and then sort alphabetically by row
    # t: pandas table, row: name of row (str in header)
    mt1 = t[row]
    mt = t.applymap(lambda x: str(x).replace("$","").replace("\\","").upper())
    s = mt.sort_values(row)
    #print(s.index)
    return t.reindex(s.index)



if __name__ == "__main__":
    # just for testing
    old = pd.read_csv("abbrev.csv",header=0,sep="\t")
    #s = list(old.sort_values("Zeichen").to_numpy())
    #print(s)
    #print(old.sort_values("Zeichen"))
    headers = list(old)
    #print(old)
    #print(headers)
    #print(s.to_string(index=False))
    s = sortTable(old,"Zeichen").to_numpy()

    #print(s_clean)
    #print(s)
    toTexTable(s,headers,"abbrev")
    print("written from abbrev.csv to abbrev.tex")
    #print(s)