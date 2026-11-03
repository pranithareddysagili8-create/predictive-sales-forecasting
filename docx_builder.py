"""
Professional Word Document (.docx) Generator for
Predictive Sales Forecasting and Business Analytics System
Generates an extensive, highly structured, 20-page A4 Technical Project Report.
"""

import os
import zipfile
import html

def escape_xml(s):
    if s is None:
        return ""
    return html.escape(str(s))

class DocxBuilder:
    def __init__(self, filename="Predictive_Sales_Forecasting_Documentation.docx"):
        self.filename = filename
        self.paragraphs = []
        self.images = []  # list of (rel_id, target_media_name, source_path)
        self.img_counter = 0

    def add_page_break(self):
        self.paragraphs.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    def add_title_block(self, title, subtitle, metadata):
        xml = [
            '<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:before="720" w:after="240"/></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:color w:val="1E3A8A"/><w:sz w:val="56"/></w:rPr><w:t>{escape_xml(title)}</w:t></w:r></w:p>',
            
            '<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:before="0" w:after="480"/></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:i/><w:color w:val="4B5563"/><w:sz w:val="28"/></w:rPr><w:t>{escape_xml(subtitle)}</w:t></w:r></w:p>',
            
            '<w:p><w:pPr><w:pBdr><w:bottom w:val="single" w:sz="18" w:space="12" w:color="2563EB"/></w:pBdr><w:spacing w:after="480"/></w:pPr></w:p>'
        ]
        for label, val in metadata:
            xml.append(
                f'<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:after="80"/></w:pPr>'
                f'<w:r><w:rPr><w:rFonts w:ascii="Calibri"/><w:b/><w:color w:val="1E293B"/><w:sz w:val="22"/></w:rPr><w:t>{escape_xml(label)}: </w:t></w:r>'
                f'<w:r><w:rPr><w:rFonts w:ascii="Calibri"/><w:color w:val="334155"/><w:sz w:val="22"/></w:rPr><w:t>{escape_xml(val)}</w:t></w:r></w:p>'
            )
        self.paragraphs.append("".join(xml))

    def add_h1(self, text):
        xml = (
            '<w:p><w:pPr><w:pStyle w:val="Heading1"/><w:spacing w:before="320" w:after="140"/><w:keepNext/>'
            '<w:pBdr><w:bottom w:val="single" w:sz="12" w:space="6" w:color="2563EB"/></w:pBdr></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:color w:val="1E3A8A"/><w:sz w:val="32"/></w:rPr><w:t>{escape_xml(text)}</w:t></w:r></w:p>'
        )
        self.paragraphs.append(xml)

    def add_h2(self, text):
        xml = (
            '<w:p><w:pPr><w:pStyle w:val="Heading2"/><w:spacing w:before="240" w:after="100"/><w:keepNext/></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:color w:val="2563EB"/><w:sz w:val="26"/></w:rPr><w:t>{escape_xml(text)}</w:t></w:r></w:p>'
        )
        self.paragraphs.append(xml)

    def add_h3(self, text):
        xml = (
            '<w:p><w:pPr><w:pStyle w:val="Heading3"/><w:spacing w:before="180" w:after="80"/><w:keepNext/></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:color w:val="374151"/><w:sz w:val="22"/></w:rPr><w:t>{escape_xml(text)}</w:t></w:r></w:p>'
        )
        self.paragraphs.append(xml)

    def add_p(self, text, bold=False, italic=False, color="1E293B", space_after=120):
        b_tag = "<w:b/>" if bold else ""
        i_tag = "<w:i/>" if italic else ""
        xml = (
            f'<w:p><w:pPr><w:spacing w:after="{space_after}" w:line="276" w:lineRule="auto"/></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>{b_tag}{i_tag}<w:color w:val="{color}"/><w:sz w:val="21"/></w:rPr><w:t>{escape_xml(text)}</w:t></w:r></w:p>'
        )
        self.paragraphs.append(xml)

    def add_bullet(self, bold_prefix, text):
        xml = (
            '<w:p><w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
            '<w:spacing w:after="80" w:line="276" w:lineRule="auto"/><w:ind w:left="360" w:hanging="240"/></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:ascii="Calibri"/><w:b/><w:color w:val="1E293B"/><w:sz w:val="21"/></w:rPr><w:t>{escape_xml(bold_prefix)}: </w:t></w:r>'
            f'<w:r><w:rPr><w:rFonts w:ascii="Calibri"/><w:color w:val="334155"/><w:sz w:val="21"/></w:rPr><w:t>{escape_xml(text)}</w:t></w:r></w:p>'
        )
        self.paragraphs.append(xml)

    def add_callout(self, title, text, border_color="2563EB", bg_color="EFF6FF"):
        xml = (
            f'<w:p><w:pPr><w:pBdr><w:left w:val="single" w:sz="24" w:space="12" w:color="{border_color}"/></w:pBdr>'
            f'<w:shd w:val="clear" w:color="auto" w:fill="{bg_color}"/>'
            f'<w:ind w:left="240" w:right="240"/><w:spacing w:before="120" w:after="120" w:line="260" w:lineRule="auto"/></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:ascii="Calibri"/><w:b/><w:color w:val="1E3A8A"/><w:sz w:val="21"/></w:rPr><w:t>{escape_xml(title)}: </w:t></w:r>'
            f'<w:r><w:rPr><w:rFonts w:ascii="Calibri"/><w:color w:val="1E293B"/><w:sz w:val="20"/></w:rPr><w:t>{escape_xml(text)}</w:t></w:r></w:p>'
        )
        self.paragraphs.append(xml)

    def add_code(self, code_text):
        lines = code_text.strip().split("\n")
        xml_lines = []
        for line in lines:
            xml_lines.append(
                '<w:p><w:pPr><w:shd w:val="clear" w:color="auto" w:fill="F8FAFC"/>'
                '<w:ind w:left="200" w:right="200"/><w:spacing w:before="20" w:after="20"/></w:pPr>'
                f'<w:r><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:color w:val="0F172A"/><w:sz w:val="18"/></w:rPr>'
                f'<w:t xml:space="preserve">{escape_xml(line)}</w:t></w:r></w:p>'
            )
        self.paragraphs.append("".join(xml_lines))

    def add_table(self, headers, rows, col_widths=None):
        num_cols = len(headers)
        if not col_widths:
            w_per_col = int(9000 / num_cols)
            col_widths = [w_per_col] * num_cols

        tbl = [
            '<w:tbl><w:tblPr><w:tblW w:w="9000" w:type="dxa"/><w:tblBorders>'
            '<w:top w:val="single" w:sz="6" w:space="0" w:color="D1D5DB"/>'
            '<w:left w:val="single" w:sz="6" w:space="0" w:color="D1D5DB"/>'
            '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="D1D5DB"/>'
            '<w:right w:val="single" w:sz="6" w:space="0" w:color="D1D5DB"/>'
            '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="E5E7EB"/>'
            '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="E5E7EB"/>'
            '</w:tblBorders></w:tblPr><w:tblGrid>'
        ]
        for w in col_widths:
            tbl.append(f'<w:gridCol w:w="{w}"/>')
        tbl.append('</w:tblGrid>')

        # Header Row
        tbl.append('<w:tr><w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>')
        for idx, h in enumerate(headers):
            tbl.append(
                f'<w:tc><w:tcPr><w:tcW w:w="{col_widths[idx]}" w:type="dxa"/>'
                '<w:shd w:val="clear" w:color="auto" w:fill="1E3A8A"/>'
                '<w:tcMar><w:top w:w="120"/><w:bottom w:w="120"/><w:left w:w="140"/><w:right w:w="140"/></w:tcMar></w:tcPr>'
                f'<w:p><w:pPr><w:spacing w:after="0"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Calibri"/><w:b/><w:color w:val="FFFFFF"/><w:sz w:val="19"/></w:rPr><w:t>{escape_xml(h)}</w:t></w:r></w:p></w:tc>'
            )
        tbl.append('</w:tr>')

        # Data Rows
        for r_idx, row in enumerate(rows):
            fill = "F9FAFB" if (r_idx % 2 == 1) else "FFFFFF"
            tbl.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>')
            for c_idx, cell in enumerate(row):
                tbl.append(
                    f'<w:tc><w:tcPr><w:tcW w:w="{col_widths[c_idx]}" w:type="dxa"/>'
                    f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
                    '<w:tcMar><w:top w:w="90"/><w:bottom w:w="90"/><w:left w:w="140"/><w:right w:w="140"/></w:tcMar></w:tcPr>'
                    f'<w:p><w:pPr><w:spacing w:after="0"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Calibri"/><w:color w:val="1E293B"/><w:sz w:val="18"/></w:rPr><w:t>{escape_xml(cell)}</w:t></w:r></w:p></w:tc>'
                )
            tbl.append('</w:tr>')

        tbl.append('</w:tbl>')
        self.paragraphs.append("".join(tbl))

    def add_image(self, source_path, caption, width_in=6.0, height_in=2.7):
        if not os.path.exists(source_path):
            return
        self.img_counter += 1
        rel_id = f"rIdImg{self.img_counter}"
        target_name = f"image_{self.img_counter}.png"
        self.images.append((rel_id, target_name, source_path))

        cx = int(width_in * 914400)
        cy = int(height_in * 914400)

        drawing_xml = (
            f'<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:before="120" w:after="60"/></w:pPr>'
            '<w:r><w:drawing>'
            '<wp:inline distT="0" distB="0" distL="0" distR="0" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">'
            f'<wp:extent cx="{cx}" cy="{cy}"/>'
            f'<wp:docPr id="{self.img_counter}" name="Picture {self.img_counter}"/>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:nvPicPr>'
            f'<pic:cNvPr id="{self.img_counter}" name="Picture {self.img_counter}"/>'
            '<pic:cNvPicPr/>'
            '</pic:nvPicPr>'
            '<pic:blipFill>'
            f'<a:blip r:embed="{rel_id}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>'
            '<a:stretch><a:fillRect/></a:stretch>'
            '</pic:blipFill>'
            '<pic:spPr>'
            '<a:xfrm>'
            '<a:off x="0" y="0"/>'
            f'<a:ext cx="{cx}" cy="{cy}"/>'
            '</a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            '</pic:spPr>'
            '</pic:pic>'
            '</a:graphicData>'
            '</a:graphic>'
            '</wp:inline>'
            '</w:drawing></w:r></w:p>'
            f'<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:after="160"/></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:ascii="Calibri"/><w:i/><w:color w:val="64748B"/><w:sz w:val="18"/></w:rPr><w:t>Figure: {escape_xml(caption)}</w:t></w:r></w:p>'
        )
        self.paragraphs.append(drawing_xml)

    def save(self):
        content_types = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
            '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
            '  <Default Extension="xml" ContentType="application/xml"/>',
            '  <Default Extension="png" ContentType="image/png"/>',
            '  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>',
            '  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>',
            '  <Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>',
            '</Types>'
        ]

        pkg_rels = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
            '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>',
            '</Relationships>'
        ]

        doc_rels = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
            '  <Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>',
            '  <Relationship Id="rIdFooter1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
        ]
        for rel_id, target_name, _ in self.images:
            doc_rels.append(f'  <Relationship Id="{rel_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{target_name}"/>')
        doc_rels.append('</Relationships>')

        styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>
        <w:sz w:val="21"/>
        <w:szCs w:val="21"/>
        <w:lang w:val="en-US"/>
      </w:rPr>
    </w:rPrDefault>
  </w:docDefaults>
</w:styles>"""

        footer_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:p>
    <w:pPr>
      <w:pBdr><w:top w:val="single" w:sz="6" w:space="4" w:color="E5E7EB"/></w:pBdr>
      <w:tabs><w:tab w:val="right" w:pos="9000"/></w:tabs>
      <w:spacing w:before="60" w:after="0"/>
    </w:pPr>
    <w:r>
      <w:rPr><w:rFonts w:ascii="Calibri"/><w:color w:val="64748B"/><w:sz w:val="17"/></w:rPr>
      <w:t>Predictive Sales Forecasting &amp; Analytics System • CSE Capstone Project</w:t>
    </w:r>
    <w:r><w:tab/></w:r>
    <w:r>
      <w:rPr><w:rFonts w:ascii="Calibri"/><w:color w:val="64748B"/><w:sz w:val="17"/></w:rPr>
      <w:t>Page </w:t>
    </w:r>
    <w:fldSimple w:instr="PAGE"/>
    <w:r>
      <w:rPr><w:rFonts w:ascii="Calibri"/><w:color w:val="64748B"/><w:sz w:val="17"/></w:rPr>
      <w:t> of </w:t>
    </w:r>
    <w:fldSimple w:instr="NUMPAGES"/>
  </w:p>
</w:ftr>"""

        document_body = "".join(self.paragraphs)
        document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
            xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
            xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
            xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
  <w:body>
    {document_body}
    <w:sectPr>
      <w:footerReference w:type="default" r:id="rIdFooter1"/>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
      <w:cols w:space="720"/>
      <w:docGrid w:linePitch="360"/>
    </w:sectPr>
  </w:body>
</w:document>"""

        with zipfile.ZipFile(self.filename, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('[Content_Types].xml', "\n".join(content_types))
            z.writestr('_rels/.rels', "\n".join(pkg_rels))
            z.writestr('word/_rels/document.xml.rels', "\n".join(doc_rels))
            z.writestr('word/styles.xml', styles_xml)
            z.writestr('word/footer1.xml', footer_xml)
            z.writestr('word/document.xml', document_xml)
            for _, target_name, src_path in self.images:
                with open(src_path, 'rb') as f:
                    z.writestr(f"word/media/{target_name}", f.read())

        print(f"Document successfully created at {self.filename}")
