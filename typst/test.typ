#import "mvar.typ": *

// a ist der namespace
#let a = loadvariables("test.txt") 
//#let a = (b: 1, bsi: 2)
Access variable via 
$ #a.b $

Access variable with unit:
$ #a.bsi $
//#a.debug

#mlogic(a.l,[Test],[Falsch])

Testing basic table behaviour:
//#set table.cell(align: left)
#table(
	columns: (50%,1in),
	stroke: (x,y) => (
		top: if (y != 0 and x >= 1) {1pt} else {(1pt + gradient.linear(..color.map.rainbow))},
		left: if (x != 0) {1pt}
	),
	align: (right, left),
	//table.vline(start: 0),
	//table.hline(stroke: 1pt),
	table.header([Test], [*Test*]),
	[$alpha_3$] ,[test],
	[$alpha_3$] ,[test],
	[$alpha_3$] ,[test],
	[$alpha_3$] ,[test],
	//table.vline(start: 0)
)

Table of abbreviations:
#include "abbrev.typ"