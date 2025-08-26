"""
LangGraph workflow nodes for the Instagram caption agent.
"""
from typing import TypedDict, Optional
import logging
from openai import OpenAI
from utils.pdf_utils import extract_text_from_pdf, PDFExtractionError
from agent.config import get_config

logger = logging.getLogger(__name__)


class WorkflowState(TypedDict):
    """State object passed between workflow nodes."""
    pdf_path: str
    extracted_text: str
    instagram_caption: str
    error: Optional[str]


def pdf_extractor_node(state: WorkflowState) -> WorkflowState:
    """
    Extract text from PDF file and update workflow state.
    
    Args:
        state: Current workflow state containing pdf_path
        
    Returns:
        Updated workflow state with extracted_text or error
    """
    logger.info(f"Starting PDF text extraction for: {state['pdf_path']}")
    
    try:
        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(state['pdf_path'])
        
        # Update state with extracted text
        state['extracted_text'] = extracted_text
        state['error'] = None
        
        if extracted_text:
            logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF")
        else:
            logger.warning("PDF extraction completed but no text was found")
            
    except FileNotFoundError as e:
        error_msg = f"PDF file not found: {e}"
        logger.error(error_msg)
        state['error'] = error_msg
        state['extracted_text'] = ""
        
    except PermissionError as e:
        error_msg = f"Permission denied accessing PDF: {e}"
        logger.error(error_msg)
        state['error'] = error_msg
        state['extracted_text'] = ""
        
    except PDFExtractionError as e:
        error_msg = f"PDF extraction failed: {e}"
        logger.error(error_msg)
        state['error'] = error_msg
        state['extracted_text'] = ""
        
    except Exception as e:
        error_msg = f"Unexpected error during PDF extraction: {e}"
        logger.error(error_msg)
        state['error'] = error_msg
        state['extracted_text'] = ""
    
    return state


def caption_generator_node(state: WorkflowState) -> WorkflowState:
    """
    Generate Instagram caption using OpenAI API and update workflow state.
    
    Args:
        state: Current workflow state containing extracted_text
        
    Returns:
        Updated workflow state with instagram_caption or error
    """
    logger.info("Starting Instagram caption generation")
    
    # Check if we have extracted text to work with
    if state.get('error'):
        logger.warning("Skipping caption generation due to previous error")
        return state
    
    extracted_text = state.get('extracted_text', '')
    if not extracted_text.strip():
        error_msg = "No text available for caption generation"
        logger.error(error_msg)
        state['error'] = error_msg
        state['instagram_caption'] = ""
        return state
    
    try:
        # Get configuration
        config = get_config()
        
        # Initialize OpenAI client
        client = OpenAI(api_key=config.openai_api_key)
        
        # Truncate text if it's too long for the API
        if len(extracted_text) > config.max_text_length:
            truncated_text = extracted_text[:config.max_text_length]
            logger.warning(f"Text truncated from {len(extracted_text)} to {config.max_text_length} characters")
        else:
            truncated_text = extracted_text
        
        # Create Instagram-optimized prompt
        prompt = f"""You are an expert social media manager. Create an engaging Instagram caption for this news article.

<Requirements>
- Keep it concise and engaging (100-300 words)
- Maintain the article's key message and tone
- Reference the author
- If the piece is opinionated, make it clear that the instagram caption is describing the opinions of the author, not the publication
- divide the caption up into different paragraphs if needed
<\Requirements>

<Example>
This is from an opinion article arguing that Morningside Heights and Harlem are two distinct Manhattan neighborhoods

<Caption>
In December, as Columbia students gathered for the annual Tree Lighting Ceremony, Columbia University Apartheid Divest (CUAD) protestors took to College Walk. On Instagram, they called the event a “distraction” from Columbia’s gate closures, which they claim “lock Harlem residents out of a public campus and shut off acres of land in the middle of Harlem.” This is a claim CUAD has often made—that Morningside Heights, where Columbia’s main campus has stood since 1897, is in the middle of Harlem.

The problem? It’s not true. Morningside Heights has always been a distinct neighborhood. Its history, geography, and development have distinguished it from Harlem for centuries. Rewriting neighborhood boundaries to fit a political narrative erases the histories of both Harlem and Morningside Heights.

Staff Editor Nicholas Baum unpacks the facts—and why mislabeling Columbia’s neighborhood is inaccurate and does a disservice to both communities.

🔗 Full article at the link in bio.
<\Caption>
<\Example>

<Example>
This is from an informative article describing how a Columbia University club brought a controversial speaker to campus
<Caption>
On Saturday, February 22, the Columbia and Barnard Black History Month (BHM) Committee hosted Dr. Umar Johnson as the keynote speaker at its Winter Soulstice event in Lerner Hall. Dr. Umar, an activist and motivational speaker, has drawn criticism for his fierce opposition to homosexuality in the black community.

The Columbia and Barnard BHM Committee marketed the event as “a cross between an indoor carnival, a dinner party, and a showcase” for students to “mingle and celebrate the joyous aspects of Black Life @ CU.”

Dr. Umar’s speech at the event did not directly address LGBTQ issues. However, several students told Sundial that they took issue with the committee’s decision to invite Dr. Umar as the keynote speaker because of his previous statements about LGBTQ people.
<\Caption>
<\Example>

Article text:
{truncated_text}

Generate only the Instagram caption, no additional commentary."""

        # Call OpenAI API
        logger.info(f"Calling OpenAI API with model: {config.openai_model}")
        response = client.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are an expert social media manager specializing in Instagram content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,  # Reasonable limit for Instagram captions
            temperature=0.7  # Some creativity but not too random
        )
        
        # Extract the generated caption
        instagram_caption = response.choices[0].message.content.strip()
        
        # Update state with generated caption
        state['instagram_caption'] = instagram_caption
        state['error'] = None
        
        logger.info(f"Successfully generated Instagram caption ({len(instagram_caption)} characters)")
        
    except ValueError as e:
        # Configuration errors
        error_msg = f"Configuration error: {e}"
        logger.error(error_msg)
        state['error'] = error_msg
        state['instagram_caption'] = ""
        
    except Exception as e:
        # OpenAI API errors and other unexpected errors
        error_msg = f"Failed to generate Instagram caption: {e}"
        logger.error(error_msg)
        state['error'] = error_msg
        state['instagram_caption'] = ""
    
    return state