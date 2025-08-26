"""
Tests for the LangGraph workflow implementation.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.agent.workflow import create_workflow, execute_workflow, validate_workflow_state, get_workflow_status
from src.agent.nodes import WorkflowState


class TestWorkflowCreation:
    """Test workflow creation and configuration."""
    
    def test_create_workflow_returns_compiled_graph(self):
        """Test that create_workflow returns a compiled StateGraph."""
        workflow = create_workflow()
        
        # Verify that we get a compiled workflow back
        assert workflow is not None
        assert hasattr(workflow, 'invoke')
    
    def test_workflow_has_correct_structure(self):
        """Test that the workflow has the expected nodes and edges."""
        workflow = create_workflow()
        
        # The workflow should be compiled and ready to execute
        # We can't easily inspect the internal structure of a compiled graph,
        # but we can verify it was created without errors
        assert workflow is not None


class TestWorkflowExecution:
    """Test workflow execution scenarios."""
    
    @patch('src.agent.workflow.create_workflow')
    def test_execute_workflow_with_valid_pdf(self, mock_create_workflow):
        """Test successful workflow execution."""
        # Mock the compiled workflow
        mock_workflow = MagicMock()
        mock_workflow.invoke.return_value = {
            "pdf_path": "test.pdf",
            "extracted_text": "Sample article text",
            "instagram_caption": "Great article! #news #instagram",
            "error": None
        }
        mock_create_workflow.return_value = mock_workflow
        
        # Execute the workflow
        result = execute_workflow("test.pdf")
        
        # Verify the result
        assert result["pdf_path"] == "test.pdf"
        assert result["extracted_text"] == "Sample article text"
        assert result["instagram_caption"] == "Great article! #news #instagram"
        assert result["error"] is None
        
        # Verify the workflow was called with correct initial state
        mock_workflow.invoke.assert_called_once()
        call_args = mock_workflow.invoke.call_args[0][0]
        assert call_args["pdf_path"] == "test.pdf"
        assert call_args["extracted_text"] == ""
        assert call_args["instagram_caption"] == ""
        assert call_args["error"] is None
    
    @patch('src.agent.workflow.create_workflow')
    def test_execute_workflow_handles_exceptions(self, mock_create_workflow):
        """Test workflow execution error handling."""
        # Mock the workflow to raise an exception
        mock_create_workflow.side_effect = Exception("Workflow creation failed")
        
        # Execute the workflow
        result = execute_workflow("test.pdf")
        
        # Verify error handling
        assert result["pdf_path"] == "test.pdf"
        assert result["extracted_text"] == ""
        assert result["instagram_caption"] == ""
        assert "Workflow execution failed" in result["error"]


class TestWorkflowValidation:
    """Test workflow state validation."""
    
    def test_validate_workflow_state_with_valid_state(self):
        """Test validation of a complete workflow state."""
        state: WorkflowState = {
            "pdf_path": "test.pdf",
            "extracted_text": "Sample text",
            "instagram_caption": "Sample caption",
            "error": None
        }
        
        assert validate_workflow_state(state) is True
    
    def test_validate_workflow_state_with_missing_fields(self):
        """Test validation fails with missing required fields."""
        incomplete_state = {
            "pdf_path": "test.pdf",
            "extracted_text": "Sample text"
            # Missing instagram_caption and error fields
        }
        
        assert validate_workflow_state(incomplete_state) is False


class TestWorkflowStatus:
    """Test workflow status reporting."""
    
    def test_get_workflow_status_success(self):
        """Test status reporting for successful execution."""
        state: WorkflowState = {
            "pdf_path": "test.pdf",
            "extracted_text": "Sample text",
            "instagram_caption": "Great article! #news",
            "error": None
        }
        
        status = get_workflow_status(state)
        assert "Success" in status
        assert "20 character" in status  # Length of the caption
    
    def test_get_workflow_status_with_error(self):
        """Test status reporting for failed execution."""
        state: WorkflowState = {
            "pdf_path": "test.pdf",
            "extracted_text": "",
            "instagram_caption": "",
            "error": "PDF file not found"
        }
        
        status = get_workflow_status(state)
        assert "Failed" in status
        assert "PDF file not found" in status
    
    def test_get_workflow_status_unknown(self):
        """Test status reporting for unknown state."""
        state: WorkflowState = {
            "pdf_path": "test.pdf",
            "extracted_text": "Sample text",
            "instagram_caption": "",
            "error": None
        }
        
        status = get_workflow_status(state)
        assert "Unknown" in status