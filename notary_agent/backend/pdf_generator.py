from jinja2 import Environment, FileSystemLoader
import pdfkit
import os

def generate_pdf(data: dict, filename_prefix: str = "deed"):
    # Setup template environment
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('deed_template.html')

    # Render filled-in HTML
    rendered_html = template.render(**data)

    # Save files
    output_dir = "generated_pdfs"
    os.makedirs(output_dir, exist_ok=True)

    html_path = os.path.join(output_dir, f"{filename_prefix}.html")
    pdf_path = os.path.join(output_dir, f"{filename_prefix}.pdf")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    # Configure path to wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    pdfkit.from_file(html_path, pdf_path, configuration=config)

    return pdf_path
