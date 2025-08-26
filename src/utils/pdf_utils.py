"""
PDF text extraction utilities for the Instagram caption agent.
"""
import os
from typing import Optional
import pdfplumber
import logging

logger = logging.getLogger(__name__)


class PDFExtractionError(Exception):
    """Custom exception for PDF extraction errors."""
    pass


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
        
    Raises:
        PDFExtractionError: If PDF cannot be processed
        FileNotFoundError: If PDF file doesn't exist
        PermissionError: If PDF file cannot be accessed
    """
    # Validate file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Check file permissions
    if not os.access(pdf_path, os.R_OK):
        raise PermissionError(f"Cannot read PDF file: {pdf_path}")
    
    # Validate it's a PDF file
    if not pdf_path.lower().endswith('.pdf'):
        raise PDFExtractionError(f"File is not a PDF: {pdf_path}")
    
    extracted_text = ""
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Check if PDF has pages
            if not pdf.pages:
                logger.warning(f"PDF file has no pages: {pdf_path}")
                return ""
            
            # Extract text from all pages
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += page_text + "\n"
                    else:
                        logger.warning(f"No text found on page {page_num} of {pdf_path}")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {e}")
                    continue
                    
    except Exception as e:
        # Handle corrupted or invalid PDF files
        if "not a valid PDF" in str(e).lower() or "corrupted" in str(e).lower():
            raise PDFExtractionError(f"PDF file is corrupted or invalid: {pdf_path}")
        else:
            raise PDFExtractionError(f"Error processing PDF file {pdf_path}: {e}")
    
    # Clean up extracted text
    extracted_text = extracted_text.strip()
    
    if not extracted_text:
        logger.warning(f"No text content extracted from PDF: {pdf_path}")
    
    return extracted_text


def validate_pdf_file(pdf_path: str) -> bool:
    """
    Validate if a file is a readable PDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        True if file is a valid, readable PDF, False otherwise
    """
    try:
        extract_text_from_pdf(pdf_path)
        return True
    except (FileNotFoundError, PermissionError, PDFExtractionError):
        return False