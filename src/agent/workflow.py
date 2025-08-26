"""
LangGraph workflow implementation for Instagram caption generation.
"""
from typing import Dict, Any
import logging
from langgraph.graph import StateGraph, END
from agent.nodes import WorkflowState, pdf_extractor_node, caption_generator_node

logger = logging.getLogger(__name__)


def create_workflow() -> StateGraph:
    """
    Create and configure the LangGraph workflow for Instagram caption generation.
    
    Returns:
        Configured StateGraph ready for execution
    """
    logger.info("Creating Instagram caption generation workflow")
    
    # Create the state graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes to the workflow
    workflow.add_node("pdf_extractor", pdf_extractor_node)
    workflow.add_node("caption_generator", caption_generator_node)
    
    # Define the workflow sequence
    workflow.set_entry_point("pdf_extractor")
    workflow.add_edge("pdf_extractor", "caption_generator")
    workflow.add_edge("caption_generator", END)
    
    # Compile the workflow
    compiled_workflow = workflow.compile()
    
    logger.info("Workflow created successfully")
    return compiled_workflow


def execute_workflow(pdf_path: str) -> Dict[str, Any]:
    """
    Execute the Instagram caption generation workflow.
    
    Args:
        pdf_path: Path to the PDF file to process
        
    Returns:
        Final workflow state containing results or errors
    """
    logger.info(f"Starting workflow execution for PDF: {pdf_path}")
    
    try:
        # Create the workflow
        workflow = create_workflow()
        
        # Initialize the workflow state
        initial_state: WorkflowState = {
            "pdf_path": pdf_path,
            "extracted_text": "",
            "instagram_caption": "",
            "error": None
        }
        
        # Execute the workflow
        logger.info("Executing workflow...")
        final_state = workflow.invoke(initial_state)
        
        # Log the results
        if final_state.get('error'):
            logger.error(f"Workflow completed with error: {final_state['error']}")
        else:
            logger.info("Workflow completed successfully")
            logger.info(f"Generated caption length: {len(final_state.get('instagram_caption', ''))}")
        
        return final_state
        
    except Exception as e:
        error_msg = f"Workflow execution failed: {e}"
        logger.error(error_msg)
        return {
            "pdf_path": pdf_path,
            "extracted_text": "",
            "instagram_caption": "",
            "error": error_msg
        }


def validate_workflow_state(state: WorkflowState) -> bool:
    """
    Validate that the workflow state contains required fields.
    
    Args:
        state: Workflow state to validate
        
    Returns:
        True if state is valid, False otherwise
    """
    required_fields = ["pdf_path", "extracted_text", "instagram_caption", "error"]
    
    for field in required_fields:
        if field not in state:
            logger.error(f"Missing required field in workflow state: {field}")
            return False
    
    return True


def get_workflow_status(state: WorkflowState) -> str:
    """
    Get a human-readable status of the workflow execution.
    
    Args:
        state: Final workflow state
        
    Returns:
        Status string describing the workflow result
    """
    if state.get('error'):
        return f"Failed: {state['error']}"
    
    if state.get('instagram_caption'):
        caption_length = len(state['instagram_caption'])
        return f"Success: Generated {caption_length} character Instagram caption"
    
    return "Unknown: Workflow completed but no caption was generated"