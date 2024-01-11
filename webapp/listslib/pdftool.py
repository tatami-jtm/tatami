import io, sys
from fpdf import FPDF
from pypdf import PdfReader, PdfWriter
import pypdfium2 as pdfium

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

def make_image(obj):
    output = io.BytesIO()
    make_writer(obj).write(output)
    pdf = pdfium.PdfDocument(output)
    bitmap = pdf[0].render(
        scale = 5,
        optimize_mode='lcd'
    )
    pil_image = bitmap.to_pil()
    return pil_image