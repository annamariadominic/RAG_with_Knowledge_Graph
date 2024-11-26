import os
import fitz  # PyMuPDF
import pypandoc

# Define the directory containing your PDFs and where to save the converted files
input_directory = "data"
output_directory = "data_md"

# Ensure output directory exists
os.makedirs(output_directory, exist_ok=True)

def convert_pdf_to_md(pdf_path, md_path):
    # Read PDF and extract text
    text_content = ""
    with fitz.open(pdf_path) as pdf_document:
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text_content += page.get_text()
    
    # Save extracted text directly as Markdown format
    with open(md_path, "w", encoding="utf-8") as md_file:
        md_file.write(text_content)
    
    print(f"Converted {pdf_path} to {md_path}")

# Process each PDF in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(input_directory, filename)
        md_filename = os.path.splitext(filename)[0] + ".md"
        md_path = os.path.join(output_directory, md_filename)
        convert_pdf_to_md(pdf_path, md_path)
