"""
Unit tests for LangGraph workflow nodes.
"""
import unittest
from unittest.mock import patch, MagicMock

from src.agent.nodes import pdf_extractor_node, caption_generator_node, WorkflowState
from src.utils.pdf_utils import PDFExtractionError


class TestPDFExtractorNode(unittest.TestCase):
    """Test cases for PDF extractor node."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_state = {
            'pdf_path': '/path/to/test.pdf',
            'extracted_text': '',
            'instagram_caption': '',
            'error': None
        }
        self.sample_text = "Sample news article content for Instagram caption generation."
    
    @patch('src.agent.nodes.extract_text_from_pdf')
    def test_pdf_extractor_node_success(self, mock_extract):
        """Test successful PDF text extraction in node."""
        mock_extract.return_value = self.sample_text
        
        result = pdf_extractor_node(self.sample_state)
        
        self.assertEqual(result['extracted_text'], self.sample_text)
        self.assertIsNone(result['error'])
        self.assertEqual(result['pdf_path'], self.sample_state['pdf_path'])
        mock_extract.assert_called_once_with('/path/to/test.pdf')
    
    @patch('src.agent.nodes.extract_text_from_pdf')
    def test_pdf_extractor_node_empty_text(self, mock_extract):
        """Test PDF extraction with no text content."""
        mock_extract.return_value = ""
        
        result = pdf_extractor_node(self.sample_state)
        
        self.assertEqual(result['extracted_text'], "")
        self.assertIsNone(result['error'])
    
    @patch('src.agent.nodes.extract_text_from_pdf')
    def test_pdf_extractor_node_file_not_found(self, mock_extract):
        """Test PDF extractor node with FileNotFoundError."""
        mock_extract.side_effect = FileNotFoundError("PDF file not found: /path/to/test.pdf")
        
        result = pdf_extractor_node(self.sample_state)
        
        self.assertEqual(result['extracted_text'], "")
        self.assertIsNotNone(result['error'])
        self.assertIn("PDF file not found", result['error'])
    
    @patch('src.agent.nodes.extract_text_from_pdf')
    def test_pdf_extractor_node_permission_error(self, mock_extract):
        """Test PDF extractor node with PermissionError."""
        mock_extract.side_effect = PermissionError("Permission denied accessing PDF")
        
        result = pdf_extractor_node(self.sample_state)
        
        self.assertEqual(result['extracted_text'], "")
        self.assertIsNotNone(result['error'])
        self.assertIn("Permission denied accessing PDF", result['error'])
    
    @patch('src.agent.nodes.extract_text_from_pdf')
    def test_pdf_extractor_node_pdf_extraction_error(self, mock_extract):
        """Test PDF extractor node with PDFExtractionError."""
        mock_extract.side_effect = PDFExtractionError("PDF file is corrupted")
        
        result = pdf_extractor_node(self.sample_state)
        
        self.assertEqual(result['extracted_text'], "")
        self.assertIsNotNone(result['error'])
        self.assertIn("PDF extraction failed", result['error'])
    
    @patch('src.agent.nodes.extract_text_from_pdf')
    def test_pdf_extractor_node_unexpected_error(self, mock_extract):
        """Test PDF extractor node with unexpected error."""
        mock_extract.side_effect = Exception("Unexpected error occurred")
        
        result = pdf_extractor_node(self.sample_state)
        
        self.assertEqual(result['extracted_text'], "")
        self.assertIsNotNone(result['error'])
        self.assertIn("Unexpected error during PDF extraction", result['error'])
    
    def test_pdf_extractor_node_state_preservation(self):
        """Test that node preserves other state fields."""
        test_state = self.sample_state.copy()
        test_state['instagram_caption'] = 'existing caption'
        
        with patch('src.agent.nodes.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = self.sample_text
            
            result = pdf_extractor_node(test_state)
            
            # Should preserve existing fields
            self.assertEqual(result['instagram_caption'], 'existing caption')
            self.assertEqual(result['pdf_path'], test_state['pdf_path'])


class TestWorkflowState(unittest.TestCase):
    """Test cases for WorkflowState TypedDict."""
    
    def test_workflow_state_structure(self):
        """Test WorkflowState has expected structure."""
        state = WorkflowState(
            pdf_path='/path/to/test.pdf',
            extracted_text='Sample text',
            instagram_caption='Sample caption',
            error=None
        )
        
        self.assertEqual(state['pdf_path'], '/path/to/test.pdf')
        self.assertEqual(state['extracted_text'], 'Sample text')
        self.assertEqual(state['instagram_caption'], 'Sample caption')
        self.assertIsNone(state['error'])
    
    def test_workflow_state_with_error(self):
        """Test WorkflowState with error message."""
        state = WorkflowState(
            pdf_path='/path/to/test.pdf',
            extracted_text='',
            instagram_caption='',
            error='Test error message'
        )
        
        self.assertEqual(state['error'], 'Test error message')


class TestCaptionGeneratorNode(unittest.TestCase):
    """Test cases for caption generator node."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_state = {
            'pdf_path': '/path/to/test.pdf',
            'extracted_text': 'Sample news article content for Instagram caption generation.',
            'instagram_caption': '',
            'error': None
        }
        self.sample_caption = "🔥 Breaking news! This article highlights important developments. What are your thoughts? #news #breaking #update"
    
    @patch('src.agent.nodes.get_config')
    @patch('src.agent.nodes.OpenAI')
    def test_caption_generator_node_success(self, mock_openai_class, mock_get_config):
        """Test successful caption generation."""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.openai_api_key = "sk-test-key"
        mock_config.openai_model = "gpt-4"
        mock_config.max_text_length = 8000
        mock_get_config.return_value = mock_config
        
        # Mock OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = self.sample_caption
        mock_client.chat.completions.create.return_value = mock_response
        
        result = caption_generator_node(self.sample_state)
        
        self.assertEqual(result['instagram_caption'], self.sample_caption)
        self.assertIsNone(result['error'])
        self.assertEqual(result['extracted_text'], self.sample_state['extracted_text'])
        
        # Verify OpenAI client was called correctly
        mock_openai_class.assert_called_once_with(api_key="sk-test-key")
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('src.agent.nodes.get_config')
    @patch('src.agent.nodes.OpenAI')
    def test_caption_generator_node_text_truncation(self, mock_openai_class, mock_get_config):
        """Test caption generation with text truncation."""
        # Mock configuration with small max_text_length
        mock_config = MagicMock()
        mock_config.openai_api_key = "sk-test-key"
        mock_config.openai_model = "gpt-4"
        mock_config.max_text_length = 50  # Small limit to trigger truncation
        mock_get_config.return_value = mock_config
        
        # Mock OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = self.sample_caption
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create state with long text
        long_text_state = self.sample_state.copy()
        long_text_state['extracted_text'] = "A" * 1000  # Long text that will be truncated
        
        result = caption_generator_node(long_text_state)
        
        self.assertEqual(result['instagram_caption'], self.sample_caption)
        self.assertIsNone(result['error'])
        
        # Verify the API was called (text should have been truncated internally)
        mock_client.chat.completions.create.assert_called_once()
    
    def test_caption_generator_node_no_text(self):
        """Test caption generation with no extracted text."""
        empty_text_state = self.sample_state.copy()
        empty_text_state['extracted_text'] = ""
        
        result = caption_generator_node(empty_text_state)
        
        self.assertEqual(result['instagram_caption'], "")
        self.assertIsNotNone(result['error'])
        self.assertIn("No text available for caption generation", result['error'])
    
    def test_caption_generator_node_whitespace_only_text(self):
        """Test caption generation with whitespace-only text."""
        whitespace_state = self.sample_state.copy()
        whitespace_state['extracted_text'] = "   \n\t   "
        
        result = caption_generator_node(whitespace_state)
        
        self.assertEqual(result['instagram_caption'], "")
        self.assertIsNotNone(result['error'])
        self.assertIn("No text available for caption generation", result['error'])
    
    def test_caption_generator_node_previous_error(self):
        """Test caption generation skips when there's a previous error."""
        error_state = self.sample_state.copy()
        error_state['error'] = "Previous PDF extraction failed"
        
        result = caption_generator_node(error_state)
        
        # Should preserve the previous error and not generate caption
        self.assertEqual(result['error'], "Previous PDF extraction failed")
        self.assertEqual(result['instagram_caption'], "")
    
    @patch('src.agent.nodes.get_config')
    def test_caption_generator_node_config_error(self, mock_get_config):
        """Test caption generation with configuration error."""
        mock_get_config.side_effect = ValueError("OPENAI_API_KEY environment variable is required")
        
        result = caption_generator_node(self.sample_state)
        
        self.assertEqual(result['instagram_caption'], "")
        self.assertIsNotNone(result['error'])
        self.assertIn("Configuration error", result['error'])
        self.assertIn("OPENAI_API_KEY", result['error'])
    
    @patch('src.agent.nodes.get_config')
    @patch('src.agent.nodes.OpenAI')
    def test_caption_generator_node_openai_api_error(self, mock_openai_class, mock_get_config):
        """Test caption generation with OpenAI API error."""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.openai_api_key = "sk-test-key"
        mock_config.openai_model = "gpt-4"
        mock_config.max_text_length = 8000
        mock_get_config.return_value = mock_config
        
        # Mock OpenAI client to raise an exception
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API rate limit exceeded")
        
        result = caption_generator_node(self.sample_state)
        
        self.assertEqual(result['instagram_caption'], "")
        self.assertIsNotNone(result['error'])
        self.assertIn("Failed to generate Instagram caption", result['error'])
        self.assertIn("API rate limit exceeded", result['error'])
    
    def test_caption_generator_node_state_preservation(self):
        """Test that node preserves other state fields."""
        test_state = self.sample_state.copy()
        test_state['pdf_path'] = '/custom/path/test.pdf'
        
        with patch('src.agent.nodes.get_config') as mock_get_config, \
             patch('src.agent.nodes.OpenAI') as mock_openai_class:
            
            # Mock configuration
            mock_config = MagicMock()
            mock_config.openai_api_key = "sk-test-key"
            mock_config.openai_model = "gpt-4"
            mock_config.max_text_length = 8000
            mock_get_config.return_value = mock_config
            
            # Mock OpenAI client and response
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.choices[0].message.content = self.sample_caption
            mock_client.chat.completions.create.return_value = mock_response
            
            result = caption_generator_node(test_state)
            
            # Should preserve existing fields
            self.assertEqual(result['pdf_path'], '/custom/path/test.pdf')
            self.assertEqual(result['extracted_text'], test_state['extracted_text'])


if __name__ == '__main__':
    unittest.main()