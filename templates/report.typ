#let input = json(bytes(sys.inputs.at("report")))

#let layout = input.at("layout")
#let heading = input.at("heading", default: (:))
#let rows = input.at("rows", default: ())

#let paper-of = (
  PAPER_A4: "a4",
  PAPER_A3: "a3",
  PAPER_B4: "jis-b4",
  PAPER_B5: "jis-b5",
)

#let align-of = (
  ALIGNMENT_LEFT: left,
  ALIGNMENT_CENTER: center,
  ALIGNMENT_RIGHT: right,
)

#let margin = layout.at("margin")
#let sizes = layout.at("fontSize")

#let element-body(element) = {
  if "text" in element { element.at("text") }
  else if "imageKey" in element { image(element.at("imageKey")) }
  else { context counter(page).display("1 / 1", both: true) }
}

#let placed(elements, alignment) = {
  let chosen = elements.filter(e => e.at("alignment") == alignment)
  if chosen.len() == 0 { return [] }
  stack(dir: ttb, spacing: 0.3em, ..chosen.map(element-body))
}

#let band(block-name, size) = {
  let blocks = layout.at("blocks", default: ()).filter(b => b.at("block") == block-name)
  if blocks.len() == 0 { return [] }
  let elements = blocks.at(0).at("elements", default: ())
  set text(size: eval(size + "pt"))
  grid(
    columns: (1fr, 1fr, 1fr),
    align: (left, center, right),
    placed(elements, "ALIGNMENT_LEFT"),
    placed(elements, "ALIGNMENT_CENTER"),
    placed(elements, "ALIGNMENT_RIGHT"),
  )
}

#set page(
  paper: paper-of.at(layout.at("paper")),
  flipped: layout.at("orientation") == "ORIENTATION_LANDSCAPE",
  margin: (
    top: eval(str(margin.at("topMm")) + "mm"),
    bottom: eval(str(margin.at("bottomMm")) + "mm"),
    left: eval(str(margin.at("leftMm")) + "mm"),
    right: eval(str(margin.at("rightMm")) + "mm"),
  ),
  header: band("BLOCK_HEADER", sizes.at("headerPt")),
  footer: band("BLOCK_FOOTER", sizes.at("footerPt")),
)

#set text(font: layout.at("fontFamily", default: "sans-serif"), size: eval(sizes.at("bodyPt") + "pt"))

#let columns = layout.at("columns", default: ()).sorted(key: c => c.at("displayOrder"))

#if columns.len() > 0 and rows.len() > 0 {
  table(
    columns: columns.map(c => eval(c.at("widthRatio") + "fr")),
    align: columns.map(c => align-of.at(c.at("alignment"), default: left)),
    stroke: 0.5pt,
    table.header(..columns.map(c => [*#c.at("columnHeading")*])),
    ..rows
      .map(row => columns.map(c => [#row.at(c.at("reportFieldName"), default: "")]))
      .flatten(),
  )
}
