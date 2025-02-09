#import "mvar.typ": *

//__fullsuite__

// this an example of a fullsuite application: automatic letter or report generation.
// this example 
#import "@preview/letter-pro:3.0.0": letter-simple

#set text(lang: "de")

#show: letter-simple.with(
  sender: (
    name: "Professor John Doe",
    address: "University of City, 50 Long Rd, A City, Florida",
    extra: [
      Telefon: #link("tel:+123456789")[+123456789]\
      E-Mail: #link("mailto:doe@example.com")[doe\@example.com]\
    ],
  ),
  
  annotations: [Urgent],
  recipient: [
		#m..name\
    #m..street_number\
    #m..zip_code
  ],
  
  reference-signs: (
    ([Matriculation number], [#m..matrnr]),
  ),
  
  date: "12. November 2014",
  subject: "Your results on the Engineering Mechanics 1 Exam",
)

Dear #m..name,

I am writing you to let you know you #m..decision the Engineering Mechanics 1 exam with Grade #m..grade. // You need to wrap [#m..passed] with square brackets, as the parser in the typst_fullsuite.py searches for "#m.."

With kind regards,
#v(1cm)
Professor Doe

#v(1fr)
*Anlagen:*
- Rechnung