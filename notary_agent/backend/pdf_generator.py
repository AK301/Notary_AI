import pdfkit
import os

def generate_pdf(deed_text: str, filename_prefix: str = "deed"):
    output_dir = "generated_pdfs"
    os.makedirs(output_dir, exist_ok=True)

    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Arial'; line-height: 1.6; padding: 20px; }}
            h1 {{ text-align: center; }}
        </style>
    </head>
    <body>
        <h1>Partnership Deed</h1>
        <pre>{deed_text}</pre>
    </body>
    </html>
    """

    html_path = os.path.join(output_dir, f"{filename_prefix}.html")
    pdf_path = os.path.join(output_dir, f"{filename_prefix}.pdf")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 🔧 Add path to wkhtmltopdf.exe manually
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

    pdfkit.from_file(html_path, pdf_path, configuration=config)

    return pdf_path