import os
from fpdf import FPDF

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def generate_sample_pdf(filename="sample.pdf"):
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, filename)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, text="Bulk Email Attachment", ln=True, align="C")
    pdf.cell(200, 10, text="This is a sample PDF for testing.", ln=True, align="C")

    pdf.output(filepath)
    print(f"Generated: {filepath}")
    return filepath


if __name__ == "__main__":
    generate_sample_pdf()
