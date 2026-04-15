// Classic book template — extends the Rusalka layout to support:
// part / chapter / subsection / subtitle / epigraph / cite-block / poem / book-image
// Multi-language: takes lang and fonts as parameters.

#let book(
  title: "",
  author: "",
  lang: "ru",
  fonts: ("PT Serif", "Times New Roman", "Libertinus Serif"),
  series-name: none,
  series-number: none,
  cover: none,
  publisher: "",
  year: "",
  isbn: "",
  annotation: [],
  body,
) = {
  set document(title: title, author: author)
  show heading.where(level: 1): it => []
  show heading.where(level: 2): it => []
  set text(
    font: fonts,
    size: 11pt,
    lang: lang,
    hyphenate: true,
  )
  set par(
    justify: true,
    leading: 0.75em,
    first-line-indent: 1.5em,
    linebreaks: "optimized",
  )
  show: it => {
    set block(spacing: 0.65em)
    it
  }

  // --- COVER ---
  if cover != none {
    page(margin: 0cm, header: none, footer: none)[#cover]
  }

  let l10n = (
    book-n: if lang == "en" { "Book" } else { "Книга" },
    series: if lang == "en" { "Series" } else { "Серия" },
    contents: if lang == "en" { "Contents" } else { "Содержание" },
    typeset: if lang == "en" {
      "Typeset from FB2 with Typst,"
    } else {
      "PDF-вёрстка выполнена из FB2-источника с помощью Typst,"
    },
  )

  // --- TITLE PAGE ---
  page(margin: (top: 4cm, bottom: 3cm, left: 2cm, right: 2cm), header: none, footer: none)[
    #set align(center)
    #if series-name != none [
      #text(size: 13pt, tracking: 0.15em)[#upper(series-name)]
      #v(0.4em)
      #text(size: 11pt)[#l10n.book-n #if series-number != none [#series-number]]
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
      #l10n.series: #series-name#if series-number != none [, #lower(l10n.book-n) #series-number] \
    ]
    #v(0.4em)
    #if lang == "en" [Source: ] else [Источник: ]#publisher, #year \
    ISBN: #isbn
    #v(1em)
    #l10n.typeset #datetime.today().display()
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

  // --- TOC ---
  page(header: none, footer: none)[
    #v(2cm)
    #align(center)[#text(size: 24pt, weight: "bold")[#l10n.contents]]
    #v(1.5cm)
    #set text(size: 11pt)
    #outline(title: none, depth: 2, indent: 1em)
  ]

  // --- MAIN BODY ---
  set page(
    paper: "a5",
    margin: (inside: 22mm, outside: 18mm, top: 22mm, bottom: 20mm),
    header: context {
      let headings = query(heading.where(level: 2))
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
      let page-num = here().page()
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

#let part(title: []) = {
  pagebreak(to: "odd", weak: true)
  heading(level: 1, outlined: true)[#title]
  v(1fr)
  align(center)[#text(size: 28pt, weight: "bold", tracking: 0.05em)[#title]]
  v(1fr)
  pagebreak(to: "odd", weak: true)
}

#let chapter(number: none, title: [], body) = {
  pagebreak(weak: true)
  heading(level: 2, outlined: true)[#if number != none [#number. ]#title]
  v(3cm)
  if number != none {
    align(center)[
      #text(size: 14pt, tracking: 0.2em, weight: "regular")[#upper(number)]
    ]
    v(0.5cm)
  }
  align(center)[
    #set par(justify: false, first-line-indent: 0em, leading: 0.5em)
    #set text(hyphenate: false)
    #text(size: 22pt, weight: "bold")[#title]
  ]
  v(2cm)
  body
}

#let subsection(level: 3, title: [], body) = {
  v(1.5em)
  let size = if level == 3 { 16pt } else if level == 4 { 13pt } else { 11pt }
  align(center)[
    #set par(justify: false, first-line-indent: 0em)
    #text(size: size, weight: "bold")[#title]
  ]
  v(0.8em)
  body
}

#let para(body) = {
  par(first-line-indent: 1.5em)[#body]
  parbreak()
}

#let subtitle(body) = {
  v(0.8em)
  align(center)[#text(weight: "bold")[#body]]
  v(0.4em)
}

#let scene-break = {
  v(1em)
  align(center)[#text(size: 14pt)[✦ ✦ ✦]]
  v(1em)
}

#let dropcap(letter, rest) = {
  set par(first-line-indent: 0em)
  box(
    baseline: 0.75em,
    text(size: 2.2em, weight: "bold", font: ("PT Serif", "Times New Roman"))[#letter],
  )
  h(0.08em)
  rest
}

#let epigraph(author: none, body) = {
  v(0.5em)
  pad(left: 30%)[
    #set par(justify: true, first-line-indent: 0em, leading: 0.8em)
    #set text(style: "italic", size: 10pt)
    #body
    #if author != none [
      #v(0.3em)
      #align(right)[— #author]
    ]
  ]
  v(0.8em)
}

#let cite-block(author: none, body) = {
  v(0.5em)
  pad(left: 2em, right: 2em)[
    #set par(justify: true, first-line-indent: 0em)
    #set text(style: "italic")
    #body
    #if author != none [
      #v(0.3em)
      #align(right)[— #author]
    ]
  ]
  v(0.8em)
}

#let poem(title: none, author: none, stanzas: ()) = {
  v(0.5em)
  align(center)[
    #set par(justify: false, first-line-indent: 0em, leading: 0.6em)
    #if title != none [
      #text(weight: "bold")[#title]
      #v(0.4em)
    ]
    #for (si, stanza) in stanzas.enumerate() [
      #for line in stanza [
        #line \
      ]
      #if si < stanzas.len() - 1 [#v(0.4em)]
    ]
    #if author != none [
      #v(0.4em)
      #text(style: "italic")[— #author]
    ]
  ]
  v(0.8em)
}

#let book-image(body) = {
  v(0.5em)
  align(center)[#body]
  v(0.5em)
}
