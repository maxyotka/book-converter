// Template for «Русалка. Поиск» PDF
// Exports: book, chapter, para, scene-break, dropcap

#let book(
  title: "",
  author: "",
  series-name: none,
  series-number: none,
  cover: none,
  publisher: "",
  year: "",
  isbn: "",
  annotation: [],
  body,
) = {
  set document(title: title, author: author, keywords: (series-name, "книга"))
  set page(
    paper: "a5",
    margin: (inside: 22mm, outside: 18mm, top: 18mm, bottom: 20mm),
  )
  set text(
    font: ("PT Serif", "Times New Roman", "Libertinus Serif"),
    size: 11pt,
    lang: "ru",
    hyphenate: true,
  )
  set par(
    justify: true,
    leading: 0.75em,
    first-line-indent: 1.5em,
    linebreaks: "optimized",
  )

  body
}

#let chapter(number: "", title: "", body) = {
  pagebreak(to: "odd", weak: true)
  v(3cm)
  if number != "" {
    align(center)[
      #text(size: 14pt, tracking: 0.2em, weight: "regular")[#upper(number)]
    ]
    v(0.5cm)
  }
  align(center)[
    #text(size: 22pt, weight: "bold")[#title]
  ]
  v(2cm)
  body
}

#let para(body) = {
  par(first-line-indent: 1.5em)[#body]
  parbreak()
}

#let scene-break = {
  v(1em)
  align(center)[#text(size: 14pt)[✦ ✦ ✦]]
  v(1em)
}

#let dropcap(body) = body  // placeholder, real impl in Task 10
