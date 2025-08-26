"""
Unit tests for PDF text extraction utilities.
"""
import os
import tempfile
import unittest
from unittest.mock import patch, mock_open, MagicMock

from src.utils.pdf_utils import (
    extract_text_from_pdf, 
    validate_pdf_file, 
    PDFExtractionError
)


class TestPDFUtils(unittest.TestCase):
    """Test cases for PDF utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_text = "Sample news article content for testing."
        self.temp_dir = tempfile.mkdtemp()
        self.valid_pdf_path = os.path.join(self.temp_dir, "test.pdf")
        self.invalid_path = os.path.join(self.temp_dir, "nonexistent.pdf")
        self.non_pdf_path = os.path.join(self.temp_dir, "test.txt")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('pdfplumber.open')
    @patch('os.path.exists')
    @patch('os.access')
    def test_extract_text_success(self, mock_access, mock_exists, mock_pdf_open):
        """Test successful text extraction from PDF."""
        # Setup mocks
        mock_exists.return_value = True
        mock_access.return_value = True
        
        mock_page = MagicMock()
        mock_page.extract_text.return_value = self.sample_text
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf
        
        # Test extraction
        result = extract_text_from_pdf(self.valid_pdf_path)
        
        # Assertions
        self.assertEqual(result.strip(), self.sample_text)
        mock_pdf_open.assert_called_once_with(self.valid_pdf_path)
        mock_page.extract_text.assert_called_once()
    
    def test_extract_text_file_not_found(self):
        """Test FileNotFoundError when PDF doesn't exist."""
        with self.assertRaises(FileNotFoundError) as context:
            extract_text_from_pdf(self.invalid_path)
        
        self.assertIn("PDF file not found", str(context.exception))
    
    @patch('os.path.exists')
    @patch('os.access')
    def test_extract_text_permission_error(self, mock_access, mock_exists):
        """Test PermissionError when PDF cannot be read."""
        mock_exists.return_value = True
        mock_access.return_value = False
        
        with self.assertRaises(PermissionError) as context:
            extract_text_from_pdf(self.valid_pdf_path)
        
        self.assertIn("Cannot read PDF file", str(context.exception))
    
    @patch('os.path.exists')
    @patch('os.access')
    def test_extract_text_invalid_file_extension(self, mock_access, mock_exists):
        """Test PDFExtractionError for non-PDF files."""
        mock_exists.return_value = True
        mock_access.return_value = True
        
        with self.assertRaises(PDFExtractionError) as context:
            extract_text_from_pdf(self.non_pdf_path)
        
        self.assertIn("File is not a PDF", str(context.exception))
    
    @patch('pdfplumber.open')
    @patch('os.path.exists')
    @patch('os.access')
    def test_extract_text_empty_pdf(self, mock_access, mock_exists, mock_pdf_open):
        """Test extraction from PDF with no pages."""
        mock_exists.return_value = True
        mock_access.return_value = True
        
        mock_pdf = MagicMock()
        mock_pdf.pages = []
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf
        
        result = extract_text_from_pdf(self.valid_pdf_path)
        
        self.assertEqual(result, "")
    
    @patch('pdfplumber.open')
    @patch('os.path.exists')
    @patch('os.access')
    def test_extract_text_no_text_content(self, mock_access, mock_exists, mock_pdf_open):
        """Test extraction from PDF with no extractable text."""
        mock_exists.return_value = True
        mock_access.return_value = True
        
        mock_page = MagicMock()
        mock_page.extract_text.return_value = None
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf
        
        result = extract_text_from_pdf(self.valid_pdf_path)
        
        self.assertEqual(result, "")
    
    @patch('pdfplumber.open')
    @patch('os.path.exists')
    @patch('os.access')
    def test_extract_text_corrupted_pdf(self, mock_access, mock_exists, mock_pdf_open):
        """Test PDFExtractionError for corrupted PDF."""
        mock_exists.return_value = True
        mock_access.return_value = True
        mock_pdf_open.side_effect = Exception("not a valid PDF")
        
        with self.assertRaises(PDFExtractionError) as context:
            extract_text_from_pdf(self.valid_pdf_path)
        
        # Check that it's either the corrupted message or the general error message
        error_msg = str(context.exception)
        self.assertTrue(
            "PDF file is corrupted or invalid" in error_msg or 
            "Error processing PDF file" in error_msg
        )
    
    @patch('pdfplumber.open')
    @patch('os.path.exists')
    @patch('os.access')
    def test_extract_text_multiple_pages(self, mock_access, mock_exists, mock_pdf_open):
        """Test extraction from multi-page PDF."""
        mock_exists.return_value = True
        mock_access.return_value = True
        
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content"
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf
        
        result = extract_text_from_pdf(self.valid_pdf_path)
        
        self.assertIn("Page 1 content", result)
        self.assertIn("Page 2 content", result)
    
    @patch('pdfplumber.open')
    @patch('os.path.exists')
    @patch('os.access')
    def test_extract_text_page_extraction_error(self, mock_access, mock_exists, mock_pdf_open):
        """Test handling of page-level extraction errors."""
        mock_exists.return_value = True
        mock_access.return_value = True
        
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.side_effect = Exception("Page extraction error")
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf
        
        result = extract_text_from_pdf(self.valid_pdf_path)
        
        # Should still get content from page 1
        self.assertIn("Page 1 content", result)
    
    @patch('src.utils.pdf_utils.extract_text_from_pdf')
    def test_validate_pdf_file_valid(self, mock_extract):
        """Test validate_pdf_file with valid PDF."""
        mock_extract.return_value = "Some text"
        
        result = validate_pdf_file(self.valid_pdf_path)
        
        self.assertTrue(result)
        mock_extract.assert_called_once_with(self.valid_pdf_path)
    
    @patch('src.utils.pdf_utils.extract_text_from_pdf')
    def test_validate_pdf_file_invalid(self, mock_extract):
        """Test validate_pdf_file with invalid PDF."""
        mock_extract.side_effect = PDFExtractionError("Invalid PDF")
        
        result = validate_pdf_file(self.valid_pdf_path)
        
        self.assertFalse(result)
    
    @patch('src.utils.pdf_utils.extract_text_from_pdf')
    def test_validate_pdf_file_not_found(self, mock_extract):
        """Test validate_pdf_file with non-existent file."""
        mock_extract.side_effect = FileNotFoundError("File not found")
        
        result = validate_pdf_file(self.invalid_path)
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()