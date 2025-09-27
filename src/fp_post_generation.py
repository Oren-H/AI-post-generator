from PIL import Image, ImageDraw, ImageFont
import os
import re


def _wrap_text(draw, text, font, max_width):
    """
    Wraps text to fit within a specified maximum width.
    This version requires the ImageDraw object to be passed as an argument.
    Returns a list of strings, where each string is a line.
    """
    lines = []
    if not text:
        return lines
    words = text.split()
    current_line = []
    for word in words:
        # Check if adding the next word exceeds max_width
        test_line = " ".join(current_line + [word])
        if draw.textbbox((0, 0), test_line, font=font)[2] <= max_width:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def _normalize_quotes(text: str) -> str:
    """
    Ensure nested quotes inside the pullout use single quotes, not double quotes,
    while preserving apostrophes inside words. Converts paired double quotes
    (straight or curly) used as quoting delimiters into single quotes.
    """
    if not text:
        return text

    normalized = text

    # Boundaries: avoid converting apostrophes inside words
    boundary_before = r'(^|[\s\(\[\{])'
    boundary_after = r'(?=[\s\)\]\}\.,;:!?]|$)'

    # Curly double quotes → single quotes when used as quoting delimiters
    def repl_curly_doubles(m):
        before, inner = m.group(1), m.group(2)
        return f"{before}'{inner}'"

    normalized = re.sub(boundary_before + r'"([^"]+)"' + boundary_after, repl_curly_doubles, normalized)

    # Straight double quotes → single quotes when used as quoting delimiters
    def repl_straight_doubles(m):
        before, inner = m.group(1), m.group(2)
        return f"{before}'{inner}'"

    normalized = re.sub(boundary_before + r'"([^"\n]+)"' + boundary_after, repl_straight_doubles, normalized)

    return normalized

def _ensure_wrapped_in_double(text: str) -> str:
    """Wrap entire text in straight double quotes if not already double-quoted."""
    if not text:
        return text
    stripped = text.strip()
    if (stripped.startswith('"') and stripped.endswith('"')) or (
        stripped.startswith('"') and stripped.endswith('"')
    ):
        # Normalize to straight doubles for rendering consistency
        return '"' + stripped.strip('""').strip('"') + '"'
    return '"' + stripped + '"'

def _draw_bold_text(draw, text, position, font, fill):
    """Draw text with simulated bold effect by drawing multiple times with slight offsets."""
    x, y = position
    # Draw the text multiple times with more offsets for heavier bold effect
    offsets = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2), (2, 1), (1, 2), (2, 2)]
    for dx, dy in offsets:
        draw.text((x + dx, y + dy), text, fill=fill, font=font)

def generate_image(quote, byline, title, save_dir=None):

    # 1. Define image dimensions and background color - The Free Press style
    img_width = 1080  # Standard Instagram post aspect ratio (square)
    img_height = 1080
    # The Free Press uses clean white/light backgrounds with dark text
    bg_color = (255, 255, 255)  # Clean white background

    # 2. Create a new image with the specified dimensions and color
    image = Image.new('RGB', (img_width, img_height), color=bg_color)

    # 3. Get a drawing context
    draw = ImageDraw.Draw(image)

    # 4. Define the text to display. This is a long paragraph to match the image.
    long_text = _ensure_wrapped_in_double(_normalize_quotes(quote))
    byline_text = "-Oren Hartstein"
    logo_text = "The Free Press"

    # 5. Load fonts - The Free Press uses very bold, heavy sans-serif fonts
    try:
        # Try to use the boldest system fonts available that match The Free Press style
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS - try to get bold variant
            "/System/Library/Fonts/Supplemental/Arial Black.ttf",  # Very bold
            "/System/Library/Fonts/Arial.ttf",      # Fallback
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux bold
            "arial.ttf"                             # Generic fallback
        ]
        
        font_main = None
        font_byline = None
        font_logo = None
        
        # Try to load specific bold variants first for main text and logo
        bold_variants = [
            ("/System/Library/Fonts/Helvetica.ttc", 1),  # Try bold index in collection
            ("/System/Library/Fonts/Supplemental/Arial Black.ttf", 0),
            ("/System/Library/Fonts/Arial.ttf", 0),
        ]
        
        for font_path, font_index in bold_variants:
            try:
                # The Free Press uses VERY large, heavy text - make it even bigger and bolder
                if font_path.endswith('.ttc'):
                    # For font collections, try to get bold variant
                    font_main = ImageFont.truetype(font_path, size=95, index=font_index)  # Even larger
                    font_logo = ImageFont.truetype(font_path, size=42, index=font_index)
                else:
                    font_main = ImageFont.truetype(font_path, size=95)  # Even larger
                    font_logo = ImageFont.truetype(font_path, size=42)
                break
            except (IOError, OSError, TypeError):
                continue
        
        # For byline, use a serif font like The Free Press does - appears to be italic
        serif_fonts = [
            ("/System/Library/Fonts/Times.ttc", 2),  # macOS Times Italic (index 2)
            ("/System/Library/Fonts/Times.ttc", 0),  # macOS Times Regular fallback
            "/System/Library/Fonts/Georgia.ttf",  # Georgia serif
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",  # Linux italic
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",  # Linux regular
            "times.ttf",  # Generic fallback
        ]
        
        for serif_item in serif_fonts:
            try:
                if isinstance(serif_item, tuple):
                    serif_path, font_index = serif_item
                    font_byline = ImageFont.truetype(serif_path, size=44, index=font_index)  # Slightly smaller
                else:
                    font_byline = ImageFont.truetype(serif_item, size=44)  # Slightly smaller
                break
            except (IOError, OSError, TypeError):
                continue
        
        # Fallback to regular loading if bold variants fail
        if font_main is None:
            for font_path in font_paths:
                try:
                    font_main = ImageFont.truetype(font_path, size=95)  # Updated size
                    font_logo = ImageFont.truetype(font_path, size=42)  # Updated size
                    break
                except (IOError, OSError):
                    continue
        
        # Fallback for byline if serif fonts fail
        if font_byline is None:
            for font_path in font_paths:
                try:
                    font_byline = ImageFont.truetype(font_path, size=44)  # Updated size
                    break
                except (IOError, OSError):
                    continue
                
        if font_main is None:
            raise IOError("No suitable font found")
        
    except IOError:
        print("Font file not found. Using default font.")
        font_main = ImageFont.load_default()
        font_byline = ImageFont.load_default()
        font_logo = ImageFont.load_default()

    # 6. Wrap the main text based on the image width with some padding
    # The Free Press uses more generous padding
    padding = 120
    wrapped_text = _wrap_text(draw, long_text, font_main, img_width - padding * 2)

    # 7. Calculate text position to center the entire block
    # Sum the height of each line using textbbox()
    quote_lines_height = sum(draw.textbbox((0, 0), line, font=font_main)[3] for line in wrapped_text)
    total_text_height = quote_lines_height # We'll add the byline and logo separately

    start_y = (img_height - total_text_height) / 2

    # 8. Draw each line of the wrapped text - The Free Press uses pure black text
    text_color = (0, 0, 0)  # Pure black for maximum contrast
    current_y = start_y

    for line in wrapped_text:
        # Use textbbox to get the width of each line for centering
        text_width = draw.textbbox((0, 0), line, font=font_main)[2]
        text_height = draw.textbbox((0, 0), line, font=font_main)[3]
        x = (img_width - text_width) / 2
        # Use bold text rendering for heavier appearance
        _draw_bold_text(draw, line, (x, current_y), font_main, text_color)
        current_y += text_height - 5  # Even tighter line spacing like The Free Press

    # 9. Draw the byline text at the bottom center - using The Free Press red color
    formatted_byline = byline
    if byline and byline.strip():
        formatted_byline = "—" + byline.lstrip("-–— ").strip()
    byline_width = draw.textbbox((0, 0), formatted_byline, font=font_byline)[2]
    byline_height = draw.textbbox((0, 0), formatted_byline, font=font_byline)[3]
    byline_x = (img_width - byline_width) / 2
    byline_y = img_height - padding + 40  # Position like in The Free Press image
    # The Free Press uses a bright red for bylines - matching the image
    byline_color = (220, 53, 69)  # Bright red matching The Free Press style
    # Use regular text (not bold effect) for the byline as it's more elegant
    draw.text((byline_x, byline_y), formatted_byline, fill=byline_color, font=font_byline)

    # 10. Add The Free Press logo at the top - exactly like in the image
    try:
        # Create "THE FP" logo text exactly like in the image
        logo_line1 = "THE"
        logo_line2 = "FP"
        
        # Use black text for the logo, positioned at top center
        logo_color = (0, 0, 0)  # Black like in the image
        
        # Calculate positioning for two-line logo
        line1_width = draw.textbbox((0, 0), logo_line1, font=font_logo)[2]
        line1_height = draw.textbbox((0, 0), logo_line1, font=font_logo)[3]
        line2_width = draw.textbbox((0, 0), logo_line2, font=font_logo)[2]
        line2_height = draw.textbbox((0, 0), logo_line2, font=font_logo)[3]
        
        # Center both lines
        line1_x = (img_width - line1_width) / 2
        line2_x = (img_width - line2_width) / 2
        
        # Position at top with proper spacing
        logo_top_margin = 60
        line1_y = logo_top_margin
        line2_y = line1_y + line1_height - 8  # Even tighter spacing for logo
        
        # Draw the two-line logo with bold effect
        _draw_bold_text(draw, logo_line1, (line1_x, line1_y), font_logo, logo_color)
        _draw_bold_text(draw, logo_line2, (line2_x, line2_y), font_logo, logo_color)

    except Exception as e:
        print(f"An error occurred while processing the branding: {e}")
        # Fallback: Use single line branding
        brand_text = "THE FP"
        brand_width = draw.textbbox((0, 0), brand_text, font=font_logo)[2]
        brand_x = (img_width - brand_width) / 2
        brand_y = 60
        draw.text((brand_x, brand_y), brand_text, fill=(0, 0, 0), font=font_logo)

    # 11. Save the image
    if save_dir:
        try:
            os.makedirs(save_dir, exist_ok=True)
        except Exception:
            # If directory creation fails, fall back to current directory
            save_dir = None
    output_path = os.path.join(save_dir, title + ".png") if save_dir else (title + ".png")
    image.save(output_path)
    print(f"Image {title} generated successfully!")
