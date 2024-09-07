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