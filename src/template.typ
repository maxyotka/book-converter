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
  // Hide heading in body flow — we draw chapter title manually; heading only registers in TOC
  show heading.where(level: 1): it => []
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

  // --- COVER ---
  if cover != none {
    page(margin: 0cm, header: none, footer: none)[
      #cover
    ]
  }

  // --- TITLE PAGE ---
  page(margin: (top: 4cm, bottom: 3cm, left: 2cm, right: 2cm), header: none, footer: none)[
    #set align(center)
    #if series-name != none [
      #text(size: 13pt, tracking: 0.15em)[#upper(series-name)]

      #v(0.4em)
      #text(size: 11pt)[Книга #series-number]

      #v(4cm)
    ]
    #text(size: 15pt, tracking: 0.05em)[#author]

    #v(1.2em)
    #text(size: 30pt, weight: "bold")[#title]

    #v(2cm)
    #line(length: 30%, stroke: 0.5pt)
  ]

  // --- COPYRIGHT ---
  page(header: none, footer: none)[
    #set align(bottom + center)
    #set text(size: 9pt)
    #author \
    «#title» \

    #if series-name != none [
      Серия: #series-name, книга #series-number \
    ]

    #v(0.4em)
    Источник: #publisher, #year \
    ISBN: #isbn

    #v(1em)
    PDF-вёрстка выполнена из FB2-источника \
    с помощью Typst, #datetime.today().display()
  ]

  // --- ANNOTATION ---
  if annotation != [] {
    page(header: none, footer: none)[
      #v(3cm)
      #set text(style: "italic", size: 11pt)
      #set par(justify: true, first-line-indent: 0em, leading: 0.85em)
      #annotation
    ]
  }

  // --- TABLE OF CONTENTS ---
  page(header: none, footer: none)[
    #v(2cm)
    #align(center)[
      #text(size: 24pt, weight: "bold")[Содержание]
    ]
    #v(1.5cm)
    #set text(size: 11pt)
    #outline(title: none, depth: 1, indent: 0em)
  ]

  // --- MAIN BODY ---
  set page(
    paper: "a5",
    margin: (inside: 22mm, outside: 18mm, top: 22mm, bottom: 20mm),
    header: context {
      let headings = query(heading.where(level: 1))
      let page-num = here().page()
      let current = headings.filter(h => h.location().page() <= page-num)
      if current.len() == 0 { return }
      set text(size: 9pt, tracking: 0.1em)
      if calc.even(page-num) [
        #align(left)[#upper(author)]
      ] else [
        #set text(style: "italic")
        #align(right)[#current.last().body]
      ]
    },
    footer: context {
      let headings = query(heading.where(level: 1))
      let page-num = here().page()
      let current = headings.filter(h => h.location().page() <= page-num)
      if current.len() == 0 { return }
      set text(size: 9pt)
      if calc.even(page-num) [
        #align(left)[#page-num]
      ] else [
        #align(right)[#page-num]
      ]
    },
  )
  body
}

#let chapter(number: "", title: "", body) = {
  pagebreak(to: "odd", weak: true)

  // Register in outline (invisible heading)
  [#heading(level: 1, outlined: true)[#if number != "" [#number. ]#title]]

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

// Hide heading at chapter location — we draw it manually above
#let _hide-heading = {}

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
