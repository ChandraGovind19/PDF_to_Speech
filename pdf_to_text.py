import pymupdf as fitz

file_path = 'BA6-Individual Reflection copy.pdf'

pdf = fitz.open(file_path)

pdf_info = pdf.metadata

# print("PDF Metadata:", pdf_info)

# Extract text from each page of the PDF and save it to a text file
def extract_text_from_pdf(pdf_file):
    out = open("output.txt", "wb")
    for page in pdf_file: 
        text = page.get_text().encode("utf8") 
        out.write(text) 
        out.write(bytes((12,))) 
    out.close()

extract_text_from_pdf(pdf)