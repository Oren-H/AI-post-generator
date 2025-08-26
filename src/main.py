#!/usr/bin/env python3
"""
Main execution interface for the Instagram caption generation agent.
"""
import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Add the src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agent.workflow import execute_workflow, get_workflow_status
from agent.config import get_config, AgentConfig


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the application.
    
    Args:
        verbose: If True, enable debug logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def validate_pdf_path(pdf_path: str) -> Path:
    """
    Validate that the PDF path exists and is readable.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Path object for the validated PDF file
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        PermissionError: If the PDF file isn't readable
        ValueError: If the path is not a PDF file
    """
    path = Path(pdf_path)
    
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {pdf_path}")
    
    if not path.suffix.lower() == '.pdf':
        raise ValueError(f"File is not a PDF: {pdf_path}")
    
    if not path.stat().st_size > 0:
        raise ValueError(f"PDF file is empty: {pdf_path}")
    
    # Check if file is readable
    try:
        with open(path, 'rb') as f:
            f.read(1)  # Try to read one byte
    except PermissionError:
        raise PermissionError(f"Permission denied reading PDF file: {pdf_path}")
    
    return path


def generate_instagram_caption(pdf_path: str, verbose: bool = False) -> str:
    """
    Main function to generate Instagram caption from PDF file.
    
    Args:
        pdf_path: Path to the PDF file containing the news article
        verbose: Enable verbose logging
        
    Returns:
        Generated Instagram caption
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        PermissionError: If the PDF file isn't readable
        ValueError: If configuration or input validation fails
        RuntimeError: If workflow execution fails
    """
    # Setup logging
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting Instagram caption generation for: {pdf_path}")
    
    try:
        # Validate configuration
        config = get_config()
        logger.info(f"Using OpenAI model: {config.openai_model}")
        
        # Validate PDF path
        validated_path = validate_pdf_path(pdf_path)
        logger.info(f"PDF file validated: {validated_path}")
        
        # Execute the workflow
        final_state = execute_workflow(str(validated_path))
        
        # Check for errors
        if final_state.get('error'):
            error_msg = f"Workflow failed: {final_state['error']}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Extract the generated caption
        instagram_caption = final_state.get('instagram_caption', '')
        if not instagram_caption:
            error_msg = "No Instagram caption was generated"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        logger.info(f"Successfully generated Instagram caption ({len(instagram_caption)} characters)")
        return instagram_caption
        
    except (FileNotFoundError, PermissionError, ValueError) as e:
        logger.error(f"Input validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise RuntimeError(f"Failed to generate Instagram caption: {e}")


def main() -> int:
    """
    Command-line interface for the Instagram caption generator.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Generate Instagram captions from news article PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s article.pdf
  %(prog)s /path/to/news/article.pdf --verbose
  %(prog)s article.pdf --output caption.txt
        """
    )
    
    parser.add_argument(
        'pdf_path',
        help='Path to the PDF file containing the news article'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file to save the generated caption (optional)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Instagram Caption Generator 1.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        # Generate the Instagram caption
        caption = generate_instagram_caption(args.pdf_path, args.verbose)
        
        # Output the caption
        if args.output:
            # Save to file
            output_path = Path(args.output)
            output_path.write_text(caption, encoding='utf-8')
            print(f"Instagram caption saved to: {output_path}")
        else:
            # Print to stdout
            print("\n" + "="*60)
            print("GENERATED INSTAGRAM CAPTION")
            print("="*60)
            print(caption)
            print("="*60)
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 1
    except (FileNotFoundError, PermissionError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"Runtime error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())