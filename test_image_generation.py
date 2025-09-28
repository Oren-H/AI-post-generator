#!/usr/bin/env python3
"""
Test file to demonstrate fp_post_generation and image_generation functionality.
This script generates sample images using both styles with example quotes and bylines.
"""

import os
import sys
from datetime import datetime

# Add src directory to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from image_generation import generate_image
from fp_post_generation import generate_image as fp_generate_image

def get_test_quotes():
    """Get the test quotes for image generation."""
    return [
        {
            "text": "In an era where information travels at the speed of light, we must remember that wisdom still moves at the pace of reflection. The most profound insights often come not from rapid consumption of data, but from the deliberate contemplation of ideas.",
            "byline": "Professor Michael Rodriguez",
            "title": "medium_quote"
        },
        {
            "text": "Democracy is not a spectator sport. It requires active participation, informed debate, and the courage to engage with ideas that challenge our preconceptions. When we retreat into echo chambers, we abandon the very principles that make democratic discourse possible. The health of our republic depends not on the volume of our voices, but on the quality of our listening.",
            "byline": "Senator Elizabeth Warren",
            "title": "long_quote"
        }
    ]

def test_original_style():
    """Test the Original (Sundial) style image generation."""
    # Create output directory for test images
    output_dir = os.path.join(os.path.dirname(__file__), "test_output")
    os.makedirs(output_dir, exist_ok=True)
    
    test_quotes = get_test_quotes()
    
    print("=" * 80)
    print("TESTING ORIGINAL (SUNDIAL) STYLE")
    print("=" * 80)
    print(f"Output directory: {output_dir}")
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for i, quote_data in enumerate(test_quotes, 1):
        quote_text = quote_data["text"]
        byline = quote_data["byline"]
        base_title = quote_data["title"]
        
        print(f"Testing Quote {i}: {base_title}")
        print(f"Text: {quote_text[:100]}...")
        print(f"Byline: {byline}")
        print()
        
        try:
            original_title = f"{base_title}_original"
            generate_image(quote_text, byline, original_title, save_dir=output_dir)
            print(f"✓ Generated Original style: {original_title}.png")
        except Exception as e:
            print(f"✗ Error generating Original style: {e}")
        
        print("-" * 40)
    
    print("=" * 80)
    print("ORIGINAL STYLE TEST COMPLETE")
    print("=" * 80)

def test_freepress_style():
    """Test the Free Press style image generation."""
    # Create output directory for test images
    output_dir = os.path.join(os.path.dirname(__file__), "test_output")
    os.makedirs(output_dir, exist_ok=True)
    
    test_quotes = get_test_quotes()
    
    print("=" * 80)
    print("TESTING FREE PRESS STYLE")
    print("=" * 80)
    print(f"Output directory: {output_dir}")
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for i, quote_data in enumerate(test_quotes, 1):
        quote_text = quote_data["text"]
        byline = quote_data["byline"]
        base_title = quote_data["title"]
        
        print(f"Testing Quote {i}: {base_title}")
        print(f"Text: {quote_text[:100]}...")
        print(f"Byline: {byline}")
        print()
        
        try:
            fp_title = f"{base_title}_freepress"
            fp_generate_image(quote_text, byline, fp_title, save_dir=output_dir)
            print(f"✓ Generated Free Press style: {fp_title}.png")
        except Exception as e:
            print(f"✗ Error generating Free Press style: {e}")
        
        print("-" * 40)
    
    print("=" * 80)
    print("FREE PRESS STYLE TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    print("AI Post Generator - Image Generation Test")
    print("This script tests both image generation styles with sample content.")
    print()
    
    try:
        test_original_style()
        print()
        test_freepress_style()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
