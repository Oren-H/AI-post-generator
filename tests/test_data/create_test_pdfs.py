"""
Script to create test PDF files for unit testing.
"""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_sample_pdf():
    """Create a sample PDF with news article content."""
    pdf_path = "tests/test_data/sample_pdfs/sample_article.pdf"
    
    # Read the text content
    with open("tests/test_data/sample_pdfs/sample_article.txt", "r") as f:
        content = f.read()
    
    # Create PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Split content into lines and add to PDF
    lines = content.split('\n')
    y_position = height - 50
    
    for line in lines:
        if y_position < 50:  # Start new page if needed
            c.showPage()
            y_position = height - 50
        
        c.drawString(50, y_position, line)
        y_position -= 20
    
    c.save()
    print(f"Created test PDF: {pdf_path}")

def create_empty_pdf():
    """Create an empty PDF for testing."""
    pdf_path = "tests/test_data/sample_pdfs/empty_article.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.showPage()  # Empty page
    c.save()
    print(f"Created empty PDF: {pdf_path}")

if __name__ == "__main__":
    create_sample_pdf()
    create_empty_pdf()