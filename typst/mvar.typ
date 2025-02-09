// typst implementation of mvar system

/*
#set text(
  font: "New Computer Modern"
)
#set math.equation(numbering: "(1)")
*/

// mitex module to parse matlab exported symbolic latex expressions 
#import "@preview/mitex:0.2.4": *
// si units
#import "@preview/unify:0.6.0": qty

//#let results = (0,1)
#let m // standard namespace for typst-fullsuite.py, needs to declared, can be overwritten.

// standard for table of abbreviations, only gets defined if there is a abbreviation table to get loaded in. Can be included using #include "abbrev.typ" at some point in your document

// splitted to also just be able to load variables from an array. See typst-fullsuite.py :)
#let parse_dict(d2a) = {
	let results = (debug: d2a)
	for (key, val, unit, description) in d2a {
		//[#key \ ]
		if "\\" in val { // detect latex, for e.g. formulas
			val = mitex(val) // currently not fully working, 
		} else if unit == "logic" or unit == "-" {
			val = val
		} else {
			// can produce problems with names being equal
			results.insert(key + "si", qty(val,unit,space: "#h(0.5mm)"))
		}
		results.insert(key, val)
		// 
	}
	return results
}


#let loadvariables(path) = {
	// hier eventuell mal anderen delimiter setzen
	let d2a = csv(path)
	
	let results = parse_dict(d2a)
	
	return results
}

// "1" for true, "0" for false, everything else just prints var (for debugging/when working with typst_fullsuite.py)
// not working in the moment, just already implement it in python when you want a decision
#let mlogic(var, tr, fa) = {
	if var == "True" {
		tr
	} else if var == "False" {
		fa
	} else {
		[(mvar logic on #var)]
	}
}
