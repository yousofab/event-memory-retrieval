"""Build the editable Persian phase-5 progress report from docs/phase5.md.

Optional dependency: python-docx. B Nazanin should be installed locally for
matching rendering. Neither the licensed font nor raw conversation data is
stored in the repository.
"""
import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/phase5.md"
DESTINATION = ROOT / "deliverables/گزارش-پژوهشی-مرحله-۵-ممیزی.docx"
FONT = "B Nazanin"


def property_flag(parent, name, value="1"):
    element = parent.find(qn(name))
    if element is None:
        element = OxmlElement(name)
        parent.append(element)
    element.set(qn("w:val"), value)


def persian_paragraph(paragraph, alignment=WD_ALIGN_PARAGRAPH.LEFT):
    # Word/LibreOffice interpret left+paragraph-bidi as the physical right edge.
    property_flag(paragraph._p.get_or_add_pPr(), "w:bidi")
    paragraph.alignment = alignment
    paragraph.paragraph_format.line_spacing = 1.17


def add_run(paragraph, value, bold=False, latin=False, size=None):
    run = paragraph.add_run(value)
    run.bold = bold
    run.font.name = "DejaVu Sans" if latin else FONT
    run.font.size = Pt(size or (9.5 if latin else 12.5))
    run.font.color.rgb = RGBColor(0, 0, 0)
    rpr = run._r.get_or_add_rPr()
    fonts = rpr.rFonts
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    for name in ("ascii", "hAnsi", "cs", "eastAsia"):
        fonts.set(qn("w:" + name), run.font.name)
    property_flag(rpr, "w:rtl", "0" if latin else "1")
    language = OxmlElement("w:lang")
    language.set(qn("w:val"), "en-US" if latin else "fa-IR")
    language.set(qn("w:bidi"), "en-US" if latin else "fa-IR")
    rpr.append(language)
    return run


def inline(paragraph, line, size=None):
    bold = False
    # Markdown emphasis/code markers are source formatting, not printed text.
    for part in re.split(r"(\*\*|`)", line):
        if part == "**":
            bold = not bold
        elif part == "`":
            continue
        else:
            for token in re.split(r"([A-Za-z][A-Za-z0-9_./:+\-=<>]*)", part):
                if token:
                    add_run(paragraph, token, bold=bold,
                            latin=bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_./:+\-=<>]*", token)),
                            size=size)


def shade(cell, fill):
    element = OxmlElement("w:shd")
    element.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(element)


def table_cell(cell, text, header, row_number, col_number):
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    properties = cell._tc.get_or_add_tcPr()
    margins = OxmlElement("w:tcMar")
    for side, twips in (("top", 70), ("bottom", 70), ("start", 100), ("end", 100)):
        item = OxmlElement("w:" + side)
        item.set(qn("w:w"), str(twips))
        item.set(qn("w:type"), "dxa")
        margins.append(item)
    properties.append(margins)
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "bottom", "left", "right", "insideH", "insideV"):
        element = OxmlElement("w:" + edge)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:color"), "D9D9D9")
        borders.append(element)
    properties.append(borders)
    if header:
        shade(cell, "E7EEF4")
    elif row_number % 2 == 0:
        shade(cell, "F7F9FC")
    p = cell.paragraphs[0]
    persian_paragraph(p, WD_ALIGN_PARAGRAPH.CENTER if col_number else WD_ALIGN_PARAGRAPH.LEFT)
    p.paragraph_format.space_after = Pt(0)
    inline(p, text, size=10.5)
    if header:
        for run in p.runs:
            run.bold = True


def add_table(document, block):
    rows = [[part.strip() for part in line.strip().strip("|").split("|")] for line in block]
    rows = [rows[0]] + rows[2:]
    table = document.add_table(rows=0, cols=len(rows[0]))
    table.autofit = True
    property_flag(table._tbl.tblPr, "w:bidiVisual")
    for index, items in enumerate(rows):
        cells = table.add_row().cells
        for col, item in enumerate(items):
            table_cell(cells[col], item, index == 0, index, col)
    document.add_paragraph().paragraph_format.space_after = Pt(0)


def setup(document):
    sec = document.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.left_margin, sec.right_margin = Cm(2.5), Cm(3)
    sec.top_margin, sec.bottom_margin = Cm(2.4), Cm(2.3)
    for name, size, before, after in (("Normal", 12.5, 0, 5), ("Title", 18, 0, 9),
                                      ("Heading 1", 15, 11, 6)):
        style = document.styles[name]
        style.font.name = FONT
        style.font.size = Pt(size)
        style.font.bold = name != "Normal"
        style.font.color.rgb = RGBColor(0, 0, 0)
        style._element.rPr.rFonts.set(qn("w:cs"), FONT)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = name != "Normal"
    title_properties = document.styles["Title"]._element.pPr
    border = title_properties.find(qn("w:pBdr"))
    if border is not None:
        title_properties.remove(border)
    footer = sec.footer.paragraphs[0]
    persian_paragraph(footer, WD_ALIGN_PARAGRAPH.CENTER)
    add_run(footer, "گزارش پژوهشی مرحله‌ی پنجم  |  صفحه ", size=10)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)


def build():
    document = Document()
    setup(document)
    document.core_properties.title = "ممیزی ساختاری و پایداری بازیابی شواهد"
    document.core_properties.subject = "گزارش پیشرفت پژوهشی مرحله‌ی پنجم"
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    code = False
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("```"):
            code = not code
            i += 1
            continue
        if line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            add_table(document, block)
            continue
        if line.startswith("# "):
            p = document.add_paragraph(style="Title")
            persian_paragraph(p)
            inline(p, line[2:], size=18)
        elif line.startswith("## "):
            p = document.add_paragraph(style="Heading 1")
            persian_paragraph(p)
            inline(p, line[3:], size=15)
        elif code:
            p = document.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(2)
            add_run(p, line, latin=True, size=9)
        else:
            p = document.add_paragraph(style="Normal")
            persian_paragraph(p)
            p.paragraph_format.first_line_indent = Cm(0.35)
            inline(p, line)
        i += 1
    DESTINATION.parent.mkdir(exist_ok=True)
    document.save(DESTINATION)
    print(DESTINATION)


if __name__ == "__main__":
    build()
