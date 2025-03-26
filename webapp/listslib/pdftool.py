import io, sys
from fpdf import FPDF
from pypdf import PdfReader, PdfWriter
import pypdfium2 as pdfium
import datetime

def load_file(filename):
    return PdfReader(filename)

def merge_files(old, new, *pages):
    output = PdfWriter()
    for i, page in enumerate(pages):
        old.pages[page].merge_page(page2=new.pages[i])
        output.add_page(old.pages[page])

    return output

def create_new():
    pdf = FPDF()
    pdf.add_page()
    return pdf

def prepare_new(obj):
    return PdfReader(io.BytesIO(obj.output()))

def make_writer(obj):
    writer = PdfWriter()
    writer.append_pages_from_reader(obj)
    return writer

def write_file(obj, filename):
    make_writer(obj).write(filename)

def make_image(obj, page=0):
    output = io.BytesIO()
    output.write(obj)
    pdf = pdfium.PdfDocument(output)
    bitmap = pdf[page].render(
        scale = 5,
        optimize_mode='lcd'
    )
    pil_image = bitmap.to_pil()
    return pil_image


def make_header_and_footer(pdfstr, group):
    reader = PdfReader(io.BytesIO(pdfstr))

    shadow_pdf = FPDF()
    shadow_pdf.set_font("Courier", "", 8)
    shadow_pdf.set_margin(0)

    for pageno in range(len(reader.pages)):
        shadow_pdf.add_page()
        shadow_pdf.text(192, 290, f"S. {pageno + 1}/{len(reader.pages)}")
        shadow_pdf.text(8, 286, group.title)
        shadow_pdf.text(8, 290, f"Stand: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}")
    
    shadow_pdf_reader = PdfReader(io.BytesIO(shadow_pdf.output()))

    pdf_io = io.BytesIO()
    out = merge_files(shadow_pdf_reader, reader, *range(len(reader.pages)))
    out.write(pdf_io)
    pdf_io.seek(0)

    return pdf_io.getvalue(), len(reader.pages)